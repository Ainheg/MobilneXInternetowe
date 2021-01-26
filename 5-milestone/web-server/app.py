from flask import Flask, request, g
from flask_hal import HAL
from flask_hal.document import Document, Embedded
from flask_hal.link import Link
from jwt import encode, decode
from dotenv import load_dotenv
from os import getenv
from uuid import uuid4
import redis
import pika
import json
from datetime import datetime

load_dotenv()
db = redis.Redis(host = getenv('REDIS_URL'), port = getenv('REDIS_PORT'), password = getenv('REDIS_PASS'), db=0, decode_responses=True)

def is_database_connected():
    return db.ping() if db else None

if is_database_connected():
    print("Podłączono do Redis")
else: 
    print("Błąd połączenia z Redis")

JWT_SECRET = getenv('JWT_SECRET')

app = Flask(__name__)
HAL(app)

## RABBITMQ

rabbitmq_creds = pika.credentials.PlainCredentials(getenv("LOGIN_MQ"), getenv("PASSWORD_MQ"))
rabbitmq_params = pika.ConnectionParameters(getenv("URL_MQ"), 5672, getenv("VH_MQ"), rabbitmq_creds)
rabbitmq_connection = pika.BlockingConnection(rabbitmq_params)

def make_invoice(packageid):
    package_info = { 'sender':f'{get_package_owner(packageid)}', 'id':f'{get_package_id(packageid)}'}
    try:
        channel = rabbitmq_connection.channel()
        channel.exchange_declare('invoices', 'fanout')
        channel.basic_publish(exchange='invoices', routing_key='', body=json.dumps(package_info))
        channel.close()
    except:
        print('Nie udało się nadać wiadomości RabbitMQ')
    print(package_info)
    return

def send_log_message(message):
    try:
        channel = rabbitmq_connection.channel()
        channel.exchange_declare('logs', 'fanout')
        channel.basic_publish(exchange='logs', routing_key='', body=message)
        channel.close()
    except:
        print('Nie udało się nadać wiadomości RabbitMQ')

###

@app.before_request
def authorization():
    auth_token = request.headers.get('Authorization','').replace('Bearer ','')
    try:
        g.authorization = decode(auth_token, JWT_SECRET, algorithms='HS256', verify=False)
    except:
        g.authorization = {}


def is_label_in_database(labelId):
    return db.hexists(labelId, "uid")

def is_package_in_database(packageid):
    return db.hexists(packageid, "uid")

def get_user_labels(username):
    keys = db.scan_iter(f"label:{username}:*")
    if keys:
        labels = list()
        for key in keys:
            label = db.hgetall(key)
            labels.append(label)
        return labels
    return None

def get_all_labels():
    keys = db.scan_iter(f"label:*")
    if keys:
        labels = list()
        for key in keys:
            label = db.hgetall(key)
            labels.append(label)
        return labels
    return None

def get_user_packages(username):
    keys = db.scan_iter(f"package:{username}:*")
    if keys:
        packages = list()
        for key in keys:
            package = db.hgetall(key)
            packages.append(package)
        return packages
    return None

def get_all_packages():
    keys = db.scan_iter(f"package:*")
    if keys:
        packages = list()
        for key in keys:
            package = db.hgetall(key)
            packages.append(package)
        return packages
    return None

def add_label_to_database(name, deliveryPointID, size):
    label = dict()
    label["name"] = name
    label["sender"] = g.authorization.get('usr')
    label["deliverto"] = deliveryPointID
    label["size"] = size
    label["uid"] = str(uuid4())
    return db.hset(f"label:{label['sender']}:{label['uid']}", mapping=label)

def add_package_to_database(key):
    package = db.hgetall(key)
    package["status"] = 'Nadana'
    delete_label_from_database(key)
    packageid = f"package:{package['sender']}:{package['uid']}"
    return db.hset(packageid, mapping=package)

def delete_label_from_database(labelid):
    keys = db.hgetall(labelid)
    for key in keys:
        db.hdel(labelid, key)
    return not is_label_in_database(labelid)
    
def get_package_status(packageid):
    return db.hget(packageid, 'status')

def get_package_owner(packageid):
    owner = db.hget(packageid, "sender")
    print(owner)
    return owner

def get_package_id(packageid):
    return db.hget(packageid, "uid")

def update_package_status_in_database(packageid):
    current_status = get_package_status(packageid)
    print(current_status)
    if current_status == "Nadana":
        return db.hset(packageid, 'status', "W drodze")
    if current_status == "W drodze":
        return db.hset(packageid, 'status', 'Dostarczona')
    if current_status == "Dostarczona":
        return -1
    return 1

def add_notification(username, message):
    notif_id = uuid4()
    db.setex(f"notification:{username}:{notif_id}", 11, message)
    print(db.get(f"notification:{username}:{notif_id}"))

@app.route('/api/labels', methods = ['GET'])
def load_labels():
    sub = g.authorization.get('sub')
    user = g.authorization.get('usr')
    iss = g.authorization.get('iss')
    if sub is None or user is None or iss is None:
        mess = "Brak autoryzacji klienta"
        send_log_message(mess)
        return {"message": mess}, 401
    if not is_database_connected():
        return {"message": "Nie można połączyć z bazą danych"}, 503
    if sub == "sender-get-labels":
        if iss != 'well-sent-web-client':
            mess = "Funkcjonalność niedostępna z tego klienta"
            send_log_message(mess)
            return {"message": mess}, 403
        labels = get_user_labels(user)
    elif sub == "courier-app":
        if iss != 'well-sent-courier-app':
            mess = "Funkcjonalność niedostępna z tego klienta"
            send_log_message(mess)
            return {"message": mess}, 403
        labels = get_all_labels()
    else:
        return {"message": "Zawartość niedostępna"}, 403
    label_list = []
    for label in labels:
        links = []
        if sub == "sender-app":
            links.append(Link('labels:delete', '/api/labels/' + label['uid']))
        if sub == "courier-app":
            links.append(Link('packages:create', '/api/packages/' + label['uid']))
        label_list.append(Document(data=label, links=links))
    document = Document(embedded={'labels':Embedded(data=label_list)})
    return document.to_json(), 200
    
@app.route('/api/labels', methods = ['POST'])
def add_label():
    user = g.authorization.get('usr')
    sub = g.authorization.get('sub')
    iss = g.authorization.get('iss')
    if user is None or sub is None or iss is None:
        mess = "Brak autoryzacji klienta"
        send_log_message(mess)
        return {"message": mess}, 401
    if sub != "sender-post-label":
        mess = "Brak autoryzacji klienta"
        send_log_message(mess)
        return {"message": mess}, 401
    if iss != 'well-sent-web-client':
        mess = "Funkcjonalność niedostępna z tego klienta"
        send_log_message(mess)
        return {"message": mess}, 403
    if not is_database_connected():
        return {"message": "Nie można połączyć z bazą danych"}, 503
    label = request.json
    if label is None:
        return {"message": "Brak etykiety"}, 400
    try:
        name = label['name']
        deliverto = label['deliverto']
        size = label['size']
    except:
        return {"message": "Niepoprawna reprezentacja etykiety"}, 400
    if not add_label_to_database(name, deliverto, size):
        return {"message": "Nie udało się zapisać etykiety"}, 500
    links = []
    links.append(Link('self', '/api/labels'))
    return Document(data = {}, links=links).to_json(), 201

@app.route('/api/labels/<labelid>', methods = ['DELETE'])
def delete_label(labelid):
    user = g.authorization.get('usr')
    sub = g.authorization.get('sub')
    iss = g.authorization.get('iss')
    if user is None or sub is None or iss is None:
        mess = "Brak autoryzacji klienta"
        send_log_message(mess)
        return {"message": mess}, 401
    if sub != "sender-delete-label":
        mess = "Brak autoryzacji klienta"
        send_log_message(mess)
        return {"message": mess}, 401
    if iss != 'well-sent-web-client':
        mess = "Funkcjonalność niedostępna z tego klienta"
        send_log_message(mess)
        return {"message": mess}, 403
    if not is_database_connected():
        return {"message": "Nie można połączyć z bazą danych"}, 503
    lid = f'label:{user}:{labelid}'
    success = False
    if is_label_in_database(lid):
        success = delete_label_from_database(lid)
    else:
        pid = f'package:{user}:{labelid}'
        if is_package_in_database(pid):
            return {"message":"Została już nadana paczka z tą etykietą"}, 410
        else:    
            return {"message":"Etykieta nie istnieje"}, 404
    if not success:
        return {"message": "Nie udało się usunąć etykiety"}, 503
    return {"message": "Pomyślnie usunięto etykietę"}, 204

@app.route('/api/packages', methods = ['GET'])
def load_packages():
    sub = g.authorization.get('sub')
    user = g.authorization.get('usr')
    iss = g.authorization.get('iss')
    if sub is None or user is None or iss is None:
        mess = "Brak autoryzacji klienta"
        send_log_message(mess)
        return {"message": mess}, 401
    if sub == "sender-get-packages":
        if iss != 'well-sent-web-client':
            mess = "Funkcjonalność niedostępna z tego klienta"
            send_log_message(mess)
            return {"message": mess}, 403
        packages = get_user_packages(user)
    elif sub == "courier-app":
        if iss != 'well-sent-courier-app':
            mess = "Funkcjonalność niedostępna z tego klienta"
            send_log_message(mess)
            return {"message": mess}, 403
        packages = get_all_packages()
    else:
        mess = "Brak autoryzacji klienta"
        send_log_message(mess)
        return {"message": mess}, 401
    if not is_database_connected():
        return {"message": "Nie można połączyć z bazą danych"}, 503
    package_list = []
    for package in packages:
        links = []
        if sub == "courier-app" and package["status"] != "Dostarczona":
            links.append(Link('packages:update_status', '/api/packages/' + package['uid']))
        package_list.append(Document(data=package, links=links))
    document = Document(embedded={'packages':Embedded(data=package_list)})
    return document.to_json(), 200

@app.route('/api/packages/<packageid>', methods = ['PUT'])
def update_package_status(packageid):
    result = 0
    user = g.authorization.get('usr')
    sub = g.authorization.get('sub')
    iss = g.authorization.get('iss')
    if user is None or sub is None or iss is None:
        mess = "Brak autoryzacji klienta"
        send_log_message(mess)
        return {"message": mess}, 401
    if sub != "courier-app":
        mess = "Brak autoryzacji klienta"
        send_log_message(mess)
        return {"message": mess}, 401
    if iss != "well-sent-courier-app":
        mess = "Funkcjonalność niedostępna z tego klienta"
        send_log_message(mess)
        return {"message": mess}, 403
    if not is_database_connected():
        return {"message": "Nie można połączyć z bazą danych"}, 503
    pkey = ""
    if sub == "courier-app":       
        package_key = db.keys(f"package:*:{packageid}")
        if len(package_key) == 1:
            pkey = package_key[0]
            result = update_package_status_in_database(package_key[0])
        elif len(package_key) > 1:
            return {"message": "Błąd serwera, wiele etykiet o tym samym id"}, 500
        else:
            return {"message": "Brak paczki o takim id"}, 404
    else:
        mess = "Funkcjonalność niedostępna z tego klienta"
        send_log_message(mess)
        return {"message": mess}, 403
    if result == 0:
        print(Document(data = {}).to_json())
        powner = get_package_owner(pkey)
        pstatus = get_package_status(pkey)
        puid = get_package_id(pkey)
        add_notification(powner, f"Paczka {puid} ma teraz status: {pstatus}")
        return Document(data = {}).to_json(), 204
    elif result == -1:
        return {"message": "Nie można zmienić statusu dostarczonej paczki"}, 400
    else:
        return {"message": "Nie udało się zmienić statusu paczki"}, 500
    
@app.route('/api/packages/<packageid>', methods = ['POST'])
def create_package(packageid):
    user = g.authorization.get('usr')
    sub = g.authorization.get('sub')
    iss = g.authorization.get('iss')
    if user is None or sub is None or iss is None:
        mess = "Brak autoryzacji klienta"
        send_log_message(mess)
        return {"message": mess}, 401
    if sub != "courier-app":
        mess = "Brak autoryzacji klienta"
        send_log_message(mess)
        return {"message": mess}, 401
    if iss != "well-sent-courier-app":
        mess = "Funkcjonalność niedostępna z tego klienta"
        send_log_message(mess)
        return {"message": mess}, 403
    if not is_database_connected():
        return {"message": "Nie można połączyć z bazą danych"}, 503
    if sub == "courier-app":
        label_key = db.keys(f"label:*:{packageid}")
        if len(label_key) == 1:
            add_package_to_database(label_key[0])
            pkey = label_key[0].replace("label", "package")
            powner = get_package_owner(pkey)
            pstatus = get_package_status(pkey)
            puid = get_package_id(pkey)
            print(f"Paczka {puid} ma teraz status: {pstatus}")
            make_invoice(pkey)
            add_notification(powner, f"Paczka {puid} ma teraz status: {pstatus}")
            links = []
            links.append(Link('self', '/labels'))
            return Document(data = {}, links=links).to_json(), 201
        elif len(label_key) > 1:
            return {"message": "Błąd serwera, wiele etykiet o tym samym id"}, 500
        else:
            return {"message": "Brak paczki o takim id"}, 404
    else:
        mess = "Brak uprawnień do wykonania tej operacji"
        send_log_message(mess)
        return {"message": mess}, 403

if __name__ == "__main__":
    app.run(port=2100)