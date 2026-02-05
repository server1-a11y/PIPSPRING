# config.py
import secrets

PORT = 3000
CONFIG_FILE = "config.json"

WEB_PASSWORD = "1Sampe100_@A"
SECRET_KEY = secrets.token_hex(16)

NETWORK_PASSPHRASE = "Pi Network"

TOPUP_TIME_WINDOW = 180
MAX_LOGS = 300
