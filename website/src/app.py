import os
from flask import Flask, render_template

app = Flask(__name__)

SERVER_IP = os.environ["SERVER_IP"]          # e.g. 192.168.1.230[web:42][web:40]
SERVER_NAME = os.environ["SERVER_NAME"]      # e.g. nas.local[web:42][web:40]

BASE_URL = os.environ.get("BASE_URL", f"http://{SERVER_IP}")[web:42][web:40]

@app.route("/")
def home():
    return render_template(
        "index.html",
        server_ip=SERVER_IP,
        server_name=SERVER_NAME,
        base_url=BASE_URL,
    )  # Variables become available in Jinja as {{ server_ip }} etc.[web:58][web:64]

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
