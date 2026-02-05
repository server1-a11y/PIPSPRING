# core/server_pool.py
import os
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from stellar_sdk import Server
from stellar_sdk.client.requests_client import RequestsClient
from core.utils import load_file_lines

# Shared HTTP session (IMPORTANT)
GLOBAL_SESSION = requests.Session()
retries = Retry(
    total=3,
    backoff_factor=0.1,
    status_forcelist=[500, 502, 503, 504]
)
adapter = HTTPAdapter(
    pool_connections=200,
    pool_maxsize=200,
    max_retries=retries
)
GLOBAL_SESSION.mount("http://", adapter)
GLOBAL_SESSION.mount("https://", adapter)


class FastRequestsClient(RequestsClient):
    def __init__(self):
        super().__init__()
        self.session = GLOBAL_SESSION


def get_server_pool(input_val):
    urls = []

    if os.path.isfile(input_val):
        urls = load_file_lines(input_val)
    elif "\n" in input_val or "," in input_val:
        urls = [
            u.strip()
            for u in input_val.replace(",", "\n").splitlines()
            if u.strip()
        ]
    else:
        if input_val.startswith("http"):
            urls = [input_val]
        elif input_val:
            urls = [f"http://{input_val}"]

    servers = []
    for u in urls:
        client = FastRequestsClient()
        servers.append(
            Server(
                horizon_url=u.rstrip("/"),
                client=client
            )
        )
    return servers
