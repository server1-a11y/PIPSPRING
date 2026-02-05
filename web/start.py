# web/start.py
import threading
from flask import request, jsonify

from state import RUNNING_TASKS, WEB_TASKS
from core.utils import gui_log, load_file_lines, save_config
from core.keys import derive_keypair_from_mnemonic
from core.server_pool import get_server_pool
from core.fee import get_network_base_fee
from runner.wallet_runner import setup_and_run_wallet


def start_route():
    data = request.json or {}
    save_config(data)

    servers_input = data.get("servers", "")
    fee_input = data.get("fee_file", "")
    mnemonics_input = data.get("mnemonics", "")
    dest_addr = data.get("dest_addr", "")
    master_seed = data.get("master_seed", "")
    memo = data.get("memo", "")

    auto_fee = data.get("auto_fee", True)
    base_fee = int(data.get("base_fee", 4_000_000))
    workers = int(data.get("workers", 500))
    timeout = int(data.get("timeout", 30))
    call_before = float(data.get("call_before", 1.0))
    latency = float(data.get("latency", 1.0))

    min_gas = float(data.get("min_gas", 1.1))
    topup_amt = float(data.get("topup_amt", 1.1))
    topup_cfg = {"threshold": min_gas, "amount": topup_amt}

    server_pool = get_server_pool(servers_input)
    if not server_pool:
        return jsonify({"status": "error", "msg": "No servers"})

    if auto_fee:
        base_fee = get_network_base_fee(server_pool[0])

    fee_kps = []
    for m in load_file_lines(fee_input):
        kp = derive_keypair_from_mnemonic(m)
        if kp:
            fee_kps.append(kp)

    if not fee_kps:
        return jsonify({"status": "error", "msg": "No fee wallets"})

    master_kp = (
        derive_keypair_from_mnemonic(master_seed)
        if master_seed else None
    )

    started = 0
    for m in load_file_lines(mnemonics_input):
        kp = derive_keypair_from_mnemonic(m)
        if not kp:
            continue

        pub = kp.public_key
        if pub in RUNNING_TASKS:
            continue

        RUNNING_TASKS.add(pub)
        WEB_TASKS[pub] = {
            "wallet": pub,
            "asset": "-",
            "amount": "-",
            "schedule": "-",
            "status": "Starting..."
        }

        t = threading.Thread(
            target=setup_and_run_wallet,
            args=(
                m,
                kp,
                server_pool,
                base_fee,
                fee_kps,
                dest_addr,
                memo,
                True,
                None,
                master_kp,
                workers,
                call_before,
                topup_cfg,
                timeout,
                latency
            ),
            daemon=True
        )
        t.start()
        started += 1

    gui_log(f"🚀 Started {started} wallets", "ok")
    return jsonify({"status": "ok", "msg": f"Started {started} wallets"})
