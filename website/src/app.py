import os
import shutil
from flask import Flask, render_template
import json
from zpool_status import ZPool

app = Flask(__name__)

SERVER_IP = os.environ["SERVER_IP"]
SERVER_NAME = os.environ["SERVER_NAME"]
BASE_URL = os.environ.get("BASE_URL", f"http://{SERVER_IP}")

def get_zfs_status(pool_name):
    zpool = ZPool(pool_name, options=["-v"])  # -v if you want verbose like zpool status -v
    status = zpool.get_status()               # this is already a Python dict
    return status

def disk_usage_gib(path):
    total, used, free = shutil.disk_usage(path)
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
        "hub": {**disk_usage_gib("/srv/data"), "note": "Main HUB"},
        "safetank": {**disk_usage_gib("/safetank/data/"), "note": "ZFS mirror"},
        "fasttank": {**disk_usage_gib("/fasttank/data/"), "note": "ZFS scratch"},
    }

    safetank_status = get_zfs_status("safetank")
    fasttank_status = get_zfs_status("fasttank")

    return render_template(
        "index.html",
        server_ip=SERVER_IP,
        server_name=SERVER_NAME,
        base_url=BASE_URL,
        disks=disks,
        safetank_status=safetank_status,
        fasttank_status=fasttank_status,
    )