import threading
from flask import request, jsonify
from datetime import datetime
from state import RUNNING_TASKS
from core.keys import derive_keypair_from_mnemonic
from core.server_pool import get_server_pool
from runner.wallet_runner import setup_and_run_wallet
from core.utils import load_file_lines

def start_route():
    data = request.json
    
    manual_ts = None
    if data.get("manual_mode"):
        try:
            dt_str = f"{data['y']}-{data['m']}-{data['d']} {data['H']}:{data['M']}:{data['S']}"
            manual_ts = datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S").timestamp()
        except: return jsonify({"status": "error", "msg": "Waktu manual tidak valid!"})

    servers = get_server_pool(data.get("servers", "http://4.194.35.14:31401"))
    fee_kps = [derive_keypair_from_mnemonic(m) for m in load_file_lines(data.get("fee_file", "")) if derive_keypair_from_mnemonic(m)]
    master_kp = derive_keypair_from_mnemonic(data.get("master_seed", ""))

    for m in load_file_lines(data.get("mnemonics", "")):
        kp = derive_keypair_from_mnemonic(m)
        if not kp or kp.public_key in RUNNING_TASKS: continue

        RUNNING_TASKS.add(kp.public_key)
        threading.Thread(
            target=setup_and_run_wallet,
            args=(m, kp, servers, int(data.get("base_fee", 4000000)), fee_kps, 
                  data.get("dest_addr", ""), data.get("memo", ""), 
                  not data.get("manual_mode"), manual_ts, master_kp,
                  float(data.get("call_before", 1.5)), 
                  {"threshold": data.get("min_gas", 1.1), "amount": data.get("topup_amt", 1.1)},
                  float(data.get("latency", 0.5))),
            daemon=True
        ).start()

    return jsonify({"status": "ok", "msg": "Sistem Berjalan!"})
