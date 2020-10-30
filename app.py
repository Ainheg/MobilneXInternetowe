from flask import Flask, render_template, url_for
app = Flask(__name__)
app.debug = False

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/sender/sign-up")
def sign_up():
    return render_template("signupPage.html")

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000)
