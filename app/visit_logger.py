import os
import json
from datetime import datetime

LOG_FOLDER = "data"
LOG_FILE = os.path.join(LOG_FOLDER, "user_visits.json")

os.makedirs(LOG_FOLDER, exist_ok=True)

def load_visit_log():
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r") as f:
            return json.load(f)
    return {}

def save_visit_log(log_data):
    with open(LOG_FILE, "w") as f:
        json.dump(log_data, f, indent=4)

def log_user_visit(name):
    name = name.lower()
    log_data = load_visit_log()
    timestamp = datetime.now().isoformat()
    if name not in log_data:
        log_data[name] = []
    log_data[name].append(timestamp)
    save_visit_log(log_data)

def user_visited_today(name):
    name = name.lower()
    log_data = load_visit_log()
    if name not in log_data:
        return False

    today = datetime.now().date()
    for visit_time in log_data[name]:
        try:
            visit_date = datetime.fromisoformat(visit_time).date()
            if visit_date == today:
                return True
        except Exception:
            continue
    return False
