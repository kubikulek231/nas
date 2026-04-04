import datetime
import json
import os
from pathlib import Path


DEFAULT_DATA_DIR = "/home/nas/nas/data/drive-status"
DEFAULT_RETENTION_DAYS = 60
POOL_KEY = "safetank_mirror"
POOL_LABEL = "SafeTank mirror"


def _valid_states(*values):
    return [value for value in values if value in (0, 1)]


def _normalize_state(entry):
    if POOL_KEY in entry:
        value = entry.get(POOL_KEY)
        return value if value in (0, 1) else None

    values = _valid_states(entry.get("sda"), entry.get("sdb"))
    if not values:
        return None

    return max(values)


def normalize_entry(entry):
    return {
        "timestamp": entry["timestamp"],
        POOL_KEY: _normalize_state(entry),
    }


def get_data_dir(create=True):
    data_dir = Path(os.environ.get("DRIVE_STATUS_DATA_DIR", DEFAULT_DATA_DIR))
    if create:
        data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir


def _month_file_name(now):
    return now.strftime("%Y-%m.json")


def get_month_file_path(now=None, create_dir=True):
    now = now or datetime.datetime.now()
    return get_data_dir(create=create_dir) / _month_file_name(now)


def _legacy_month_file_path(now=None):
    now = now or datetime.datetime.now()
    return Path(__file__).resolve().parent / _month_file_name(now)


def _load_entries(path):
    with path.open("r", encoding="utf-8") as file_handle:
        payload = json.load(file_handle)

    return [normalize_entry(entry) for entry in payload if "timestamp" in entry]


def load_current_month_entries(now=None):
    now = now or datetime.datetime.now()
    month_file = get_month_file_path(now=now)
    if month_file.exists():
        return _load_entries(month_file)

    legacy_file = _legacy_month_file_path(now=now)
    if legacy_file.exists():
        return _load_entries(legacy_file)

    return []


def append_entry(entry, now=None):
    now = now or datetime.datetime.now()
    data = load_current_month_entries(now=now)
    data.append(normalize_entry(entry))

    month_file = get_month_file_path(now=now)
    with month_file.open("w", encoding="utf-8") as file_handle:
        json.dump(data, file_handle, indent=2)


def load_recent_history(limit_days=None):
    limit_days = limit_days or int(
        os.environ.get("DRIVE_STATUS_RETENTION_DAYS", DEFAULT_RETENTION_DAYS)
    )
    cutoff = datetime.datetime.now() - datetime.timedelta(days=limit_days)
    data_dir = get_data_dir(create=False)

    candidates = []
    if data_dir.exists():
        candidates.extend(sorted(data_dir.glob("????-??.json")))

    if not candidates:
        candidates.extend(sorted(Path(__file__).resolve().parent.glob("????-??.json")))

    history = []
    for path in candidates:
        history.extend(_load_entries(path))

    return [
        entry
        for entry in history
        if datetime.datetime.fromisoformat(entry["timestamp"]) >= cutoff
    ]


def prune_old_files(now=None):
    now = now or datetime.datetime.now()
    retention_days = int(
        os.environ.get("DRIVE_STATUS_RETENTION_DAYS", DEFAULT_RETENTION_DAYS)
    )
    cutoff = now - datetime.timedelta(days=retention_days)
    data_dir = get_data_dir(create=False)
    if not data_dir.exists():
        return

    for path in data_dir.glob("????-??.json"):
        try:
            year, month = map(int, path.stem.split("-"))
            file_date = datetime.datetime(year, month, 1)
        except ValueError:
            continue

        if file_date < cutoff:
            path.unlink()