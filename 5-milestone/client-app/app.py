from flask import Flask, render_template, url_for, request, flash, make_response, session, jsonify
from werkzeug.exceptions import HTTPException
from bcrypt import hashpw, gensalt, checkpw
from flask_session import Session
from os import getenv
from dotenv import load_dotenv
from datetime import datetime, timedelta
from uuid import uuid4
from jwt import encode, decode
from validation import *
import redis
import requests
import json

import pika
import json



load_dotenv()
#redislabs
db = redis.Redis(host = getenv('REDIS_URL'), port = getenv('REDIS_PORT'), password = getenv('REDIS_PASS'), db=0, decode_responses=False)
#redis lokalny
#db = redis.Redis(host = '192.168.0.222', port = 6379, db=0)

if db.ping():
    print("Podłączono do Redis")
else: 
    print("Błąd połączenia z Redis")

app = Flask(__name__)
SESSION_TYPE = 'redis'
SESSION_REDIS = db
SESSION_COOKIE_SECURE = False
#Przeglądarki blokują ciastka z tagiem Secure
#wysłane z http, więc w wersji nie-heroku jest False
app.config.from_object(__name__)
app.secret_key = getenv('SECRET_KEY')
JWT_SECRET = getenv('JWT_SECRET')
API_URL = getenv('API_URL')
ses = Session(app)

### KAMIEŃ 5 ###
### RABBITMQ ###

rabbitmq_creds = pika.credentials.PlainCredentials(getenv("LOGIN_MQ"), getenv("PASSWORD_MQ"))
rabbitmq_params = pika.ConnectionParameters(getenv("URL_MQ"), 5672, getenv("VH_MQ"), rabbitmq_creds)
rabbitmq_connection = pika.BlockingConnection(rabbitmq_params)

def send_log_message(message):
    try:
        channel = rabbitmq_connection.channel()
        channel.exchange_declare('logs', 'fanout')
        channel.basic_publish(exchange='logs', routing_key='', body=message)
        channel.close()
    except:
        print('Nie udało się nadać wiadomości RabbitMQ')

### /KAMIEŃ 5 ###

### KAMIEŃ 4 ###
### OAUTH ###

from authlib.integrations.flask_client import OAuth
from six.moves.urllib.parse import urlencode
oauth = OAuth(app)
auth0 = oauth.register(
    'auth0',
    client_id=getenv('AUTH0_CLIENTID'),
    client_secret=getenv('AUTH0_SECRET'),
    api_base_url=getenv('AUTH0_DOMAIN'),
    access_token_url=getenv('AUTH0_DOMAIN') + '/oauth/token',
    authorize_url=getenv('AUTH0_DOMAIN') + '/authorize',
    client_kwargs={
        'scope': 'openid profile email',
    },
)

@app.errorhandler(Exception)
def handle_auth_error(ex):
    response = jsonify(message=str(ex))
    response.status_code = (ex.code if isinstance(ex, HTTPException) else 500)
    return response

@app.route('/callback')
def callback_handling():
    auth0.authorize_access_token()
    resp = auth0.get('userinfo')
    userinfo = resp.json()
    print(userinfo)
    session['oauth_payload'] = userinfo
    session['username'] = userinfo['sub']
    session['nickname'] = userinfo['nickname']
    print(session)
    return redirect(url_for('dashboard'))

@app.route('/login-auth0', methods=['GET'])
def login_auth0():
    return auth0.authorize_redirect(redirect_uri=url_for('callback_handling', _external=True))

### POWIADOMIENIA ###

def get_user_notifications(username):
    if not is_database_connected():
        return None
    keys = db.scan_iter(f"notification:{username}:*")
    if keys:
        notifs = list()
        for key in keys:
            notif = db.get(key)
            print(notif)
            notifs.append(notif.decode())
        return notifs
    return None

@app.route("/notifications", methods = ["GET"])
def get_notifications():
    try:
        user = session['username']
    except:
        return {'message':'no authorization'}, 401
    notifications = get_user_notifications(user)
    if notifications is None:
        return {'message':'No new notifications'}, 204
    print(notifications)
    return json.dumps(notifications), 200

### /KAMIEŃ 4 ###

def is_database_connected():
    return db.ping() if db else None

def is_user_in_database(username):
    if not is_database_connected():
        flash("Błąd połączenia z bazą danych")
        return None
    return db.hexists(f"user:{username}", "password")

def generate_token(sub):
    payload = {
        'iss': 'well-sent-web-client',
        'sub': sub,
        'usr': session['username'],
        'aud': 'well-sent-web-service',
        'exp': datetime.utcnow() + timedelta(seconds = 30)
    }
    token = encode(payload, JWT_SECRET, algorithm='HS256')
    print(token)
    return token

def register_user(username, password, firstname, lastname, email, address):
    if not is_database_connected():
        flash("Błąd połączenia z bazą danych")
        return False
    salt = gensalt(12)
    hashed = hashpw(password.encode(), salt)
    user = dict()
    user["password"] = hashed
    user["email"] = email
    user["firstname"] = firstname
    user["lastname"] = lastname
    user["address"] = address
    success = False
    if db.hset(f"user:{username}", mapping=user) == 5:
        success = True
    return success

def verify_user(username, password):
    if not is_database_connected():
        flash("Błąd połączenia z bazą danych")
        return False
    hashed = db.hget(f"user:{username}", "password")
    if not hashed:
        print(f"No password for {username}")
        return False
    return checkpw(password.encode(), hashed)

def redirect(url, status=301):
    response = make_response("", status)
    response.headers['Location'] = url
    return response

def current_user_info():
    if 'nickname' in session:
        return f'Jesteś zalogowany jako <a href="{url_for("dashboard")}">{session["nickname"]}</a>'
    return f'Nie jesteś zalogowany'

def is_user_logged_in():
    return 'username' in session

def load_labels():
    token = generate_token('sender-get-labels')
    head = {'Authorization': f'Bearer {token.decode()}'}  
    try:  
        response = requests.get(API_URL + '/labels', headers=head)
        if not response.status_code == 200: 
            flash("Ładowanie etykiet: " + str(response.status_code) + ' ' + response.json()['message'])
            return []
        labels = []
        response = response.json()
        labels = response['_embedded']['labels']
    except Exception:
        flash("Nie udało się nawiązać połączenia z API, spróbuj później (być może instancja heroku jest uśpiona)")
        send_log_message("Nie można nawiązać połączenia z API")
        return []
    return labels

def load_packages():
    token = generate_token('sender-get-packages')
    head = {'Authorization': f'Bearer {token.decode()}'} 
    try:  
        response = requests.get(API_URL + '/packages', headers=head)
        if not response.status_code == 200: 
            flash("Ładowanie paczek: " + str(response.status_code) + ' ' + response.json()['message'])
            return []
        packages = []
        response = response.json()
        packages = response['_embedded']['packages']
    except Exception:
        flash("Nie udało się nawiązać połączenia z API, spróbuj później (być może instancja heroku jest uśpiona)")
        send_log_message("Nie można nawiązać połączenia z API")
        return []
    return packages

def get_delivery_points():
    #Można by było też pobierać je z bazy, jednak uznałem, że w tym momencie byłaby to niepotrzebna komplikacja
    return ["WS-1", "WS-2", "WS-3"]

def add_label_to_database(name, deliveryPointID, size):
    label = {
        "name":name,
        "deliverto":deliveryPointID,
        "size":size
    }
    token = generate_token('sender-post-label')
    head = {'Authorization': f'Bearer {token.decode()}'}
    try: 
        response = requests.post(API_URL + '/labels', headers=head, json=label)
        if response.status_code == 201:
            return True
        else:
            flash(str(response.status_code) + ' ' + response.json()['message'])
            return False
    except Exception:
        flash("Nie udało się nawiązać połączenia z API")
        send_log_message("Nie można nawiązać połączenia z API")
        return False

def delete_label_from_database(labelid):
    token = generate_token('sender-delete-label')
    head = {'Authorization': f'Bearer {token.decode()}'}
    try: 
        response = requests.delete(API_URL + f'/labels/{labelid}', headers=head)
        if response.status_code == 204:
            return True
        else:
            flash(str(response.status_code) + ' ' + response.json()['message'])
            return False
    except Exception:
        flash("Nie udało się nawiązać połączenia z API")
        send_log_message("Nie można nawiązać połączenia z API")
        return False

@app.context_processor
def pass_to_templates():
    return {"user_logged_in":is_user_logged_in, "user_info":current_user_info}

@app.after_request
def add_headers(r):
    r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    r.headers["Pragma"] = "no-cache"
    r.headers["Expires"] = "0"
    return r

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/sender/register", methods = ["GET"])
def sign_up():
    return render_template("signupPage.html")

@app.route("/sender/register", methods = ["POST"])
def sign_up_process():
    error = False
    username = request.form.get("login")
    if not username:
        flash("Nie podano nazwy użytkownika")
        error = True
    elif not username_validation(username):
        flash("Nazwa użytkownika niepoprawna")
        error = True
    email = request.form.get("email")
    if not email:
        flash("Nie podano adresu e-mail")
        error = True
    elif not email_validation(email):
        flash("Adres e-mail niepoprawny")
        error = True
    firstname = request.form.get("firstname")
    if not firstname:
        flash("Nie podano imienia")
        error = True
    elif not name_validation(firstname):
        flash("Imię niepoprawne")
        error = True
    lastname = request.form.get("lastname")
    if not lastname:
        flash("Nie podano nazwiska")
        error = True
    elif not name_validation(lastname):
        flash("Nazwisko niepoprawne")
        error = True
    password = request.form.get("password")
    if not password:
        flash("Nie podano hasła")
        error = True
    elif not password_validation(password):
        flash("Hasło niepoprawne")
        error = True
    repeatPassword = request.form.get("repeatPassword")
    if not repeatPassword:
        flash("Nie powtórzono hasła")
        error = True
    if password != repeatPassword:
        flash("Hasła się nie zgadzają")
        error = True
    address = request.form.get("address")
    if not address:
        flash("Nie podano adresu")
        error = True
    elif not address_validation(address):
        flash("Adres zawiera niedozwolone znaki")
        error = True
    if error:
        return redirect(url_for("sign_up"))
    if is_user_in_database(username):
        flash(f"Użytkownik {username} jest już zarejestrowany")
        return redirect(url_for("sign_up"))
    if not (register_user(username, password, firstname, lastname, email, address)):
        flash("Błąd przy rejestracji użytkownika")
        return redirect(url_for("sign_up"))
    return redirect(url_for("sign_in"))

@app.route("/sender/login", methods = ["GET"])
def sign_in():
    return render_template("loginPage.html")

@app.route("/sender/login", methods = ["POST"])
def sign_in_process():
    username = request.form.get("login")
    print(username)
    if not username:
        flash("Nie podano nazwy użytkownika")
    password = request.form.get("password")
    print(password)
    if not password:
        print("Nie ma hasła")
        flash("Nie podano hasła")
        return redirect(url_for("sign_in"))
    if not (verify_user(username, password)):
        print("Nie zgadza się")
        flash("Niepoprawna kombinacja nazwy uzytkownika i hasła")
        return redirect(url_for("sign_in"))
    session["username"] = username
    print(session["username"])
    session["nickname"] = username
    session["login-time"] = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    print(session['login-time'])
    return redirect(url_for('dashboard'))

@app.route("/sender/logout", methods = ["GET"])
def logout():
    try:
        oauth = 'oauth_payload' in session
    except:
        oauth = False
    if oauth:
        session.clear()
        params = {'returnTo': url_for('index', _external=True), 'client_id': auth0.client_id}
        return redirect(auth0.api_base_url + '/v2/logout?' + urlencode(params))
    session.clear()
    return redirect(url_for('index'))

@app.route("/sender/dashboard", methods = ["GET"])
def dashboard():
    if not is_user_logged_in():
        flash("Obszar niedostępny dla niezalogowanych użytkowników")
        return redirect(url_for('sign_in'))
    labels = load_labels()
    packages = load_packages()
    return render_template("dashboard.html", labels=labels, packages=packages, get_delivery_points=get_delivery_points)

@app.route("/sender/register/username-check/<username>", methods = ["GET"])
def check_username(username):
    if is_user_in_database(username):
        return {'available':"no"}
    else:
        return {'available':"yes"}

@app.route("/sender/new-label", methods = ["POST"])
def new_label():
    error = False
    name = request.form.get("name")
    if not name:
        flash("Nie podano adresata")
        error = True
    elif not label_name_validation(name):
        flash("Niedozwolone znaki w nazwie adresata")
        error = True
    address = request.form.get("address")
    if not address:
        flash("Nie wybrano skrytki docelowej")
        error = True
    elif address not in get_delivery_points():
        flash("Wybrana skrytka nie istnieje")
        error = True
    size = request.form.get("size")
    if not size:
        flash("Nie wybrano rozmiaru paczki")
        error = True
    elif size not in ["S", "M", "L"]:
        flash("Wybrany rozmiar nie istnieje")
        error = True
    if error:
        return redirect(url_for("dashboard"))
    if not add_label_to_database(name, address, size):
        flash("Wystąpił błąd przy dodawaniu etykiety")
    return redirect(url_for("dashboard"))

@app.route("/sender/delete-label/<labelID>", methods = ["POST"])
def delete_label(labelID):
    if not is_user_logged_in():
        flash("Obszar niedostępny dla niezalogowanych użytkowników")
        return redirect(url_for("sign_in"))
    success = delete_label_from_database(labelID)
    if success:
        flash("Pomyślnie usunięto etykietę")
    else:
        flash("Wystąpił błąd")
    return redirect(url_for("dashboard"))

if __name__ == "__main__":
    app.run(port=5000)
