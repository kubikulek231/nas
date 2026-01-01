import os
import shutil
from flask import Flask, render_template

app = Flask(__name__)

SERVER_IP = os.environ["SERVER_IP"]
SERVER_NAME = os.environ["SERVER_NAME"]
BASE_URL = os.environ.get("BASE_URL", f"http://{SERVER_IP}")

def disk_usage_gib(path):
    total, used, free = shutil.disk_usage(path)  # bytes[web:175][web:196]
    return {
        "path": path,
        "total_gib": total / (1024**3),
        "used_gib": used / (1024**3),
        "free_gib": free / (1024**3),
        "percent": used / total * 100,
    }

@app.route("/")
def home():
    disks = {
        "hub": disk_usage_gib("/srv/data"),
        "safe": disk_usage_gib("/srv/data/safe"),
        "fast": disk_usage_gib("/srv/data/fast"),
    }  # Each path resolves to its underlying filesystem/mount.[web:194][web:179]

    return render_template(
        "index.html",
        server_ip=SERVER_IP,
        server_name=SERVER_NAME,
        base_url=BASE_URL,
        disks=disks,
    )
