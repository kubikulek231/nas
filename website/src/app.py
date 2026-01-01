from flask import Flask, render_template

app = Flask(__name__)

BASE_URL = "http://YOUR_NAS_IP_OR_HOSTNAME"  # e.g. http://192.168.1.230

@app.route("/")
def home():
    return render_template("index.html", base_url=BASE_URL)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
