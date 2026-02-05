import time, concurrent.futures
from state import WEB_TASKS, RUNNING_TASKS, WALLET_ACTIVE, WALLET_LOCK
from core.utils import gui_log
from automation.topup import perform_auto_topup

def lifecycle_orchestrator(target_ts, prebuilt_txs, server_pool, master_kp, fee_pairs, topup_cfg, base_fee, pub_key_id, latency_offset):
    fire_time = target_ts - float(latency_offset)
    topup_done = False

    try:
        while pub_key_id in RUNNING_TASKS:
            remaining = fire_time - time.time()
            if remaining <= 0: break

            if pub_key_id in WEB_TASKS:
                WEB_TASKS[pub_key_id]["status"] = f"T-Minus: {remaining:.2f}s"

            if remaining < 150 and not topup_done:
                perform_auto_topup(server_pool, master_kp, fee_pairs, topup_cfg["threshold"], topup_cfg["amount"], base_fee)
                topup_done = True

            if remaining > 0.5: time.sleep(0.1)
            elif remaining > 0.05: time.sleep(0.01)
            else: pass # Busy wait untuk presisi milidetik

        if pub_key_id in WEB_TASKS: WEB_TASKS[pub_key_id]["status"] = "🚀 FIRING!!!"
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=len(prebuilt_txs)) as ex:
            futures = [ex.submit(server_pool[p["target_server_index"]].submit_transaction, p["tx_obj"]) for p in prebuilt_txs]
            concurrent.futures.wait(futures, timeout=5)

        gui_log(f"✅ {pub_key_id[:6]} executed.", "ok")
        if pub_key_id in WEB_TASKS: WEB_TASKS[pub_key_id]["status"] = "Claimed"

    finally:
        with WALLET_LOCK:
            WALLET_ACTIVE.discard(pub_key_id)
