import os
from flask import Flask, render_template, jsonify
from drive_history import POOL_KEY, POOL_LABEL, load_recent_history
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
    history = load_recent_history()
    series = [
        {
            "id": POOL_KEY,
            "label": POOL_LABEL,
            "points": [
                {
                    "timestamp": entry["timestamp"],
                    "state": entry.get(POOL_KEY),
                }
                for entry in history
                if entry.get(POOL_KEY) in (0, 1)
            ],
        }
    ]
    return jsonify({"series": series})
