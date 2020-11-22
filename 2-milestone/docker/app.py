from flask import Flask, render_template, url_for, request, flash, make_response, session
from bcrypt import hashpw, gensalt, checkpw
from flask_session import Session
from os import getenv
from dotenv import load_dotenv
from datetime import datetime
from uuid import uuid4
from validation import *
import redis


load_dotenv()
#redislabs
db = redis.Redis(host = getenv('REDIS_URL'), port = getenv('REDIS_PORT'), password = getenv('REDIS_PASS'), db=0)
#redis lokalny
#db = redis.Redis(host = '192.168.0.222', port = 6379, db=0)

if db.ping():
    print("Podłączono do Redis")
else: 
    print("Błąd połączenia z Redis")

app = Flask(__name__)
SESSION_TYPE = 'redis'
SESSION_REDIS = db
#SESSION_COOKIE_SECURE = True
#Przeglądarki blokują ciastka z tagiem Secure
#wysłane z http
app.config.from_object(__name__)
app.secret_key = getenv('SECRET_KEY')
ses = Session(app)

def is_database_connected():
    return db.ping() if db else None

def is_user_in_database(username):
    if not is_database_connected():
        flash("Błąd połączenia z bazą danych")
        return None
    return db.hexists(f"user:{username}", "password")

def is_label_in_database(labelId):
    if not is_database_connected():
        flash("Błąd połączenia z bazą danych")
        return None
    return db.hexists(labelId, "uid")

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
    if 'username' in session:
        return f'Jesteś zalogowany jako <a href="{url_for("dashboard")}">{session["username"]}</a>'
    return f'Nie jesteś zalogowany'

def is_user_logged_in():
    return 'username' in session

def load_labels():
    if not is_database_connected():
        flash("Błąd połączenia z bazą danych")
        return None
    keys = db.scan_iter(f"{session['username']}:*")
    if keys:
        labels = list()
        for key in keys:
            label = dict()
            label["name"] = db.hget(key, 'name').decode()
            label["deliverto"] = db.hget(key, 'deliverto').decode()
            label["size"] = db.hget(key, 'size').decode()
            label["uid"] = db.hget(key, 'uid').decode()
            label["key"] = key
            labels.append(label)
        return labels
    return ["Jeszcze tu nic nie ma."]

def get_delivery_points():
    #Można by było też pobierać je z bazy, jednak uznałem, że w tym momencie byłaby to niepotrzebna komplikacja
    return ["WS-1", "WS-2", "WS-3"]

def add_label_to_database(name, deliveryPointID, size):
    if not is_database_connected():
        flash("Błąd połączenia z bazą danych")
        return None
    if not is_user_logged_in():
        return None
    label = dict()
    label["name"] = name
    label["deliverto"] = deliveryPointID
    label["size"] = size
    label["uid"] = str(uuid4())
    return db.hset(f"{session['username']}:{label['uid']}", mapping=label)

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
    if not username:
        flash("Nie podano nazwy użytkownika")
    password = request.form.get("password")
    if not password:
        flash("Nie podano hasła")
        return redirect(url_for("sign_in"))
    if not (verify_user(username, password)):
        flash("Niepoprawna kombinacja nazwy uzytkownika i hasła")
        return redirect(url_for("sign_in"))
    session["username"] = username
    session["login-time"] = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    return redirect(url_for('dashboard'))

@app.route("/sender/logout", methods = ["GET"])
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route("/sender/dashboard", methods = ["GET"])
def dashboard():
    if not is_user_logged_in():
        flash("Obszar niedostępny dla niezalogowanych użytkowników")
        return redirect(url_for('sign_in'))
    return render_template("dashboard.html", load_labels=load_labels, get_delivery_points=get_delivery_points)

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
    if not session["username"] in labelID:
        flash("Próbowałeś/aś usunąć nie swoją etykietę")
        return redirect(url_for("dashboard"))
    if is_label_in_database(labelID):
        keys = db.hgetall(labelID)
        for key in keys:
            db.hdel(labelID, key)
        if is_label_in_database(labelID):
            flash("Nie udało się usunąć etykiety")
        return redirect(url_for("dashboard"))

if __name__ == "__main__":
    app.run()
