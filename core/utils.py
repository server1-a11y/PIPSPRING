# core/utils.py
import os
import json
from datetime import datetime
from decimal import Decimal
from config import CONFIG_FILE, MAX_LOGS
from state import WEB_LOGS, LOG_LOCK

def load_config():
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f)
    except:
        pass
    return {}

def save_config(data):
    current = load_config()
    current.update(data)
    with open(CONFIG_FILE, 'w') as f:
        json.dump(current, f, indent=4)

def gui_log(text, color="default"):
    ts = datetime.now().strftime("%H:%M:%S")
    with LOG_LOCK:
        WEB_LOGS.append({"ts": ts, "msg": text, "type": color})
        if len(WEB_LOGS) > MAX_LOGS:
            WEB_LOGS.pop(0)

def sanitize_amount(value):
    try:
        d = Decimal(str(value)).quantize(Decimal("0.000001"))
        return format(d, "f") if d > 0 else None
    except:
        return None

def load_file_lines(input_val):
    if os.path.isfile(input_val):
        with open(input_val, "r") as f:
            return [l.strip() for l in f if l.strip()]
    return [l.strip() for l in input_val.splitlines() if l.strip()]
