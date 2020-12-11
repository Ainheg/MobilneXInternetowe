
from flask import Flask

from flask_hal import HAL, document


app = Flask(__name__)
HAL(app)  # Initialise HAL


@app.route('/hello')
def hello():
    return document.Document(data={
        'message': 'Hello World'
    }).to_json()

@app.route('/hello/<name>')
def hello_n(name):
    return document.Document(data={
        'message': f'Hello {name}'
    }).to_json()

if __name__ == "__main__":
    app.run(debug=True, port=2137)