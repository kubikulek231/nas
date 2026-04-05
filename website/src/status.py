import os
import shutil
from zpool_status import ZPool, MissingPoolError

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
    try:
        z = ZPool(pool_name, options=["-v"])
    except (MissingPoolError, Exception) as e:
        return {
            "state": "UNAVAILABLE",
            "status": f"Pool is unavailable: {str(e)}",
            "action": "Check pool status with 'zpool status' command",
            "scrub": None,
            "healthy": False,
            "bad_devices": [],
        }
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