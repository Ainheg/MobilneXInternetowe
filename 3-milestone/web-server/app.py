from flask import Flask, request, g
from flask_hal import HAL
from flask_hal.document import Document, Embedded
from flask_hal.link import Link
from jwt import encode, decode
from dotenv import load_dotenv
from os import getenv
from uuid import uuid4
import redis

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

@app.before_request
def authorization():
    auth_token = request.headers.get('Authorization','').replace('Bearer ','')
    try:
        g.authorization = decode(auth_token, JWT_SECRET, algorithms='HS256', verify=False)
    except:
        g.authorization = {}

def is_label_in_database(labelId):
    return db.hexists(labelId, "uid")

def get_user_labels(username):
    keys = db.scan_iter(f"label:{username}:*")
    if keys:
        labels = list()
        for key in keys:
            label = dict()
            label["name"] = db.hget(key, 'name')
            label["deliverto"] = db.hget(key, 'deliverto')
            label["size"] = db.hget(key, 'size')
            label["uid"] = db.hget(key, 'uid')
            label["status"] = db.hget(key, 'status')
            label["key"] = key
            labels.append(label)
        return labels
    return None

def get_all_labels():
    keys = db.scan_iter(f"label:*")
    if keys:
        labels = list()
        for key in keys:
            label = dict()
            label["name"] = db.hget(key, 'name').decode()
            label["deliverto"] = db.hget(key, 'deliverto').decode()
            label["size"] = db.hget(key, 'size').decode()
            label["uid"] = db.hget(key, 'uid').decode()
            label["status"] = db.hget(key, 'status').decode()
            label["key"] = key
            labels.append(label)
        return labels
    return None


def add_label_to_database(name, deliveryPointID, size):
    label = dict()
    label["name"] = name
    label["deliverto"] = deliveryPointID
    label["size"] = size
    label["status"] = 'nie nadana' 
    label["uid"] = str(uuid4())
    return db.hset(f"label:{g.authorization.get('usr')}:{label['uid']}", mapping=label)

def delete_label_from_database(labelid):
    keys = db.hgetall(labelid)
    for key in keys:
        db.hdel(labelid, key)
    return not is_label_in_database(labelid)
    
def get_label_status(labelid):
    print(labelid)
    print(db.hget(labelid, 'status'))
    return db.hget(labelid, 'status')

@app.route('/api/labels', methods = ['GET'])
def load_labels():
    sub = g.authorization.get('sub')
    user = g.authorization.get('usr')
    if sub is None or user is None:
        return {"message": "Brak autoryzacji"}, 401
    if sub == "sender-app":
        labels = get_user_labels(user)
    elif sub == "courier-app":
        labels = get_all_labels()
    else:
        return {"message": "Zawartość niedostępna"}, 403
    if not is_database_connected():
        return {"message": "Nie można połączyć z bazą danych"}, 503
    label_list = []
    for label in labels:
        links = []
        links.append(Link('self', '/labels/' + label['uid']))
        links.append(Link('delete', '/labels/' + label['uid']))
        labeldata = { 'uid':label['uid'], 'name':label['name'], 'deliverto':label['deliverto'], 'size':label['size'], 'status':label['status'] }
        label_list.append(Embedded(data = labeldata, links = links))
    document = Document(embedded={'labels':Embedded(data=label_list)})
    #print(document.to_json())
    return document.to_json(), 200
    
@app.route('/api/labels', methods = ['POST'])
def add_label():
    user = g.authorization.get('usr')
    if user is None:
        return {"message": "Brak autoryzacji"}, 401
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
    links.append(Link('self', '/labels'))
    return Document(data = {}, links=links).to_json(), 200

@app.route('/api/labels/<labelid>', methods = ['DELETE'])
def delete_label(labelid):
    user = g.authorization.get('usr')
    if user is None:
        return {"message": "Brak autoryzacji"}, 401
    if not is_database_connected():
        return {"message": "Nie można połączyć z bazą danych"}, 503
    labelid = f'label:{user}:{labelid}'
    success = False
    if is_label_in_database(labelid):
        if get_label_status(labelid) == 'nie nadana':
            success = delete_label_from_database(labelid)
        else:
            return {"message":"Nie można usunąć etykiety nadanej paczki"}, 403
    else:
        return {"message":"Etykieta nie istnieje lub nie jesteś jej właścicielem"}, 404
    if not success:
        return {"message": "Nie udało się usunąć etykiety"}, 503
    return {"message": "Pomyślnie usunięto etykietę"}, 204

@app.route('/api/labels/<labelid>', methods = ['PUT'])
def update_label_status(labelid):

    #TODO
    
    sub = g.authorization.get('sub')
    if sub is None:
        return {"message": "Brak autoryzacji"}, 401
    if sub == "courier-app":
        update_label_status(labelid)
    else:
        return {"message": "Brak uprawnień do wykonania tej operacji"}, 403
    if not is_database_connected():
        return {"message": "Nie można połączyć z bazą danych"}, 503
    
    

if __name__ == "__main__":
    app.run(debug=True, port=2137)