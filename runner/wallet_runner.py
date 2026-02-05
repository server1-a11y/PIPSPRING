import time
from datetime import datetime
from state import RUNNING_TASKS, WEB_TASKS, WALLET_ACTIVE, WALLET_LOCK
from core.claimables import get_claimables_for_claimant, choose_claimable, get_unlock_time, get_asset_code
from tx.builder import build_signed_tx
from automation.lifecycle import lifecycle_orchestrator
from core.utils import gui_log, sanitize_amount

def setup_and_run_wallet(mnemonic, kp, server_pool, base_fee, fee_kps, dest_addr, memo_text, is_auto, manual_ts, master_kp, call_before, topup_cfg, latency_offset):
    pub_key = kp.public_key
    while pub_key in RUNNING_TASKS:
        try:
            WEB_TASKS[pub_key] = {"wallet": pub_key, "asset": "Pi", "amount": "-", "schedule": "-", "status": "Scanning..."}
            
            records = get_claimables_for_claimant(server_pool[0], pub_key)
            chosen = choose_claimable(records, pub_key)
            
            if not chosen and is_auto:
                WEB_TASKS[pub_key]["status"] = "Waiting for data..."
                time.sleep(10); continue

            if not is_auto and manual_ts:
                execute_ts = manual_ts - float(call_before)
                schedule_str = datetime.fromtimestamp(manual_ts).strftime("%H:%M:%S")
            elif chosen:
                unlock = get_unlock_time(chosen, pub_key)
                execute_ts = (unlock.timestamp() if unlock else time.time()) - float(call_before)
                schedule_str = unlock.strftime("%H:%M:%S") if unlock else "Ready"
            else:
                execute_ts = time.time(); schedule_str = "Now"

            WEB_TASKS[pub_key].update({
                "amount": chosen['amount'] if chosen else "0",
                "schedule": schedule_str,
                "status": "Preparing TXs..."
            })

            prebuilt = []
            if chosen:
                for i, f_kp in enumerate(fee_kps):
                    tx = build_signed_tx(server_pool, {
                        "unlock_id": chosen["id"], 
                        "amount": sanitize_amount(float(chosen['amount']) - 0.01),
                        "claimant_kp": kp, "fee_kp": f_kp, "base_fee": base_fee,
                        "dest": dest_addr, "memo": memo_text, "execute_ts": execute_ts
                    }, i)
                    if tx: prebuilt.append(tx)

            if not prebuilt:
                WEB_TASKS[pub_key]["status"] = "Build Error"; time.sleep(10); continue

            with WALLET_LOCK:
                if pub_key in WALLET_ACTIVE: time.sleep(2); continue
                WALLET_ACTIVE.add(pub_key)

            lifecycle_orchestrator(execute_ts, prebuilt, server_pool, master_kp, fee_kps, topup_cfg, base_fee, pub_key, latency_offset)
            break 

        except Exception as e:
            gui_log(f"Error {pub_key[:6]}: {e}", "err")
            time.sleep(5)
