import os
import datetime
import json
from flask import Flask, render_template, jsonify
from status import summarize_pool, disk_usage_gib

app = Flask(__name__)

SERVER_IP = os.environ["SERVER_IP"]
SERVER_NAME = os.environ["SERVER_NAME"]
BASE_URL = os.environ.get("BASE_URL", f"http://{SERVER_IP}")

@app.route("/")
def home():
    safetank_status = summarize_pool("safetank")
    fasttank_status = summarize_pool("fasttank")

    disks = {
        "hub": {
            **disk_usage_gib("/srv/data"),
            "note": "Main HUB",
            "zfs": None,
        },
        "safetank": {
            **disk_usage_gib("/safetank/data/"),
            "note": None,
            "zfs": safetank_status,
        },
        "fasttank": {
            **disk_usage_gib("/fasttank/data/"),
            "note": None,
            "zfs": fasttank_status,
        },
    }

    return render_template(
        "index.html",
        server_ip=SERVER_IP,
        server_name=SERVER_NAME,
        base_url=BASE_URL,
        disks=disks,
    )

@app.route("/api/drive-status")
def drive_status():
    current_time = datetime.datetime.now()
    month_file = current_time.strftime("%Y-%m.json")
    data_file = os.path.join(os.path.dirname(__file__), month_file)
    if os.path.exists(data_file):
        with open(data_file, 'r') as f:
            data = json.load(f)
    else:
        data = []
    return jsonify(data)
