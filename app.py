from flask import Flask
import threading
from mail_listener import start_listener

app = Flask(__name__)

@app.route("/")
def home():
    return "Auto reply system running"

def start_background():

    t = threading.Thread(target=start_listener)

    t.daemon = True

    t.start()

if __name__ == "__main__":

    start_background()

    app.run(
        host="0.0.0.0",
        port=8080
    )