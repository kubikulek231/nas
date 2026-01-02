import os
import shutil
from flask import Flask, render_template
import json
from zpool_status import ZPool

app = Flask(__name__)

SERVER_IP = os.environ["SERVER_IP"]
SERVER_NAME = os.environ["SERVER_NAME"]
BASE_URL = os.environ.get("BASE_URL", f"http://{SERVER_IP}")
MOCK_ZFS = False

def summarize_pool(pool_name):
    if MOCK_ZFS:
        # simple deterministic mock, you can customize per pool_name
        if pool_name == "safetank":
            return {
                "state": "DEGRADED",
                "status": "One or more devices has experienced an error.",
                "action": "Replace the faulted device and run a scrub.",
                "scrub": "scrub repaired 0B in 0 days 00:10:23 with 0 errors on Sun Jan  2 22:00:00 2026",
                "healthy": False,
                "bad_devices": [
                    {
                        "name": "sda",
                        "state": "DEGRADED",
                        "read": 0,
                        "write": 0,
                        "cksum": 12,
                    }
                ],
            }
        elif pool_name == "fasttank":
            return {
                "state": "ONLINE",
                "status": "The pool is formatted using a legacy on-disk format.",
                "action": "Upgrade the pool using 'zpool upgrade'.",
                "scrub": "scrub repaired 0B in 0 days 00:05:02 with 0 errors on Sun Jan  2 21:00:00 2026",
                "healthy": True,
                "bad_devices": [],
            }
        else:
            return {
                "state": "ONLINE",
                "status": "All datasets are healthy.",
                "action": None,
                "scrub": None,
                "healthy": True,
                "bad_devices": [],
            }

    # real call
    z = ZPool(pool_name, options=["-v"])
    s = z.get_status()

    state = s.get("state")
    status_text = s.get("status")
    action = s.get("action")
    scrub = s.get("scrub")

    bad_devices = []

    def walk(devs):
        for d in devs or []:
            d_state = d.get("state")
            if d_state and d_state != "ONLINE":
                bad_devices.append({
                    "name": d.get("name"),
                    "state": d_state,
                    "read": d.get("read"),
                    "write": d.get("write"),
                    "cksum": d.get("cksum"),
                })
            if "devices" in d:
                walk(d["devices"])

    walk(s.get("config", []))

    healthy = (state == "ONLINE" and not bad_devices)

    return {
        "state": state,
        "status": status_text,
        "action": action,
        "scrub": scrub,
        "healthy": healthy,
        "bad_devices": bad_devices,
    }


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
