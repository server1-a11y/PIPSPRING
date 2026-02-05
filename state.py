# state.py
import threading

RUNNING_TASKS = set()
WEB_LOGS = []
WEB_TASKS = {}

LOG_LOCK = threading.Lock()
SEQUENCE_LOCK = threading.Lock()

# state.py
WALLET_ACTIVE = set()
WALLET_LOCK = threading.Lock()
