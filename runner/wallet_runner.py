# runner/wallet_runner.py
import time
import concurrent.futures
from datetime import datetime

from state import RUNNING_TASKS, WEB_TASKS
from core.utils import gui_log, sanitize_amount
from core.keys import derive_keypair_from_mnemonic
from automation.lifecycle import lifecycle_orchestrator
from core.claimables import (
    get_claimables_for_claimant,
    choose_claimable,
    get_unlock_time,
    get_asset_code
)
from tx.builder import build_tx_params, build_signed_tx
from state import WALLET_ACTIVE, WALLET_LOCK


def setup_and_run_wallet(
    mnemonic,
    kp,
    server_pool,
    base_fee,
    fee_pairs,
    dest_addr,
    memo_text,
    is_auto_detect,
    manual_ts,
    master_kp,
    prep_workers,
    call_before,
    topup_cfg,
    tx_timeout,
    latency_offset
):
    pub_key = kp.public_key

    while pub_key in RUNNING_TASKS:
        try:
            WEB_TASKS[pub_key] = {
                "wallet": pub_key,
                "asset": "Scanning...",
                "amount": "...",
                "schedule": "Checking...",
                "status": "Scanning Claims..."
            }

            records = get_claimables_for_claimant(server_pool[0], pub_key)
            chosen = choose_claimable(records, pub_key)

            if not chosen:
                WEB_TASKS[pub_key]["status"] = "Finished (No Data)"
                break

            asset = get_asset_code(chosen)
            amount = f"{float(chosen['amount']):.6f}"

            if not is_auto_detect and manual_ts:
                execute_ts = manual_ts - call_before
                schedule = f"MANUAL {datetime.fromtimestamp(manual_ts)}"
            else:
                unlock = get_unlock_time(chosen, pub_key)
                if unlock:
                    execute_ts = unlock.timestamp() - call_before
                    schedule = unlock.astimezone().strftime("%Y-%m-%d %H:%M:%S")
                else:
                    execute_ts = time.time()
                    schedule = "Ready"

            WEB_TASKS[pub_key].update({
                "asset": asset,
                "amount": amount,
                "schedule": schedule,
                "status": "Building TXs..."
            })

            raw_amt = float(chosen["amount"])
            send_amt = sanitize_amount(
                raw_amt - 1.0 if raw_amt > 1.01 else raw_amt - 0.01
            ) or "0.000001"

            params = [
                build_tx_params(
                    chosen["id"],
                    send_amt,
                    kp,
                    fp,
                    base_fee,
                    tx_timeout,
                    dest_addr,
                    memo_text,
                    execute_ts
                )
                for fp in fee_pairs
            ]

            prebuilt = []
            with concurrent.futures.ThreadPoolExecutor(max_workers=prep_workers) as ex:
                for f in concurrent.futures.as_completed(
                    [ex.submit(build_signed_tx, server_pool, p, i)
                     for i, p in enumerate(params)]
                ):
                    r = f.result()
                    if r:
                        prebuilt.append(r)

            if not prebuilt:
                WEB_TASKS[pub_key]["status"] = "Build Error"
                time.sleep(5)
                continue

            WEB_TASKS[pub_key]["status"] = f"Queued ({len(prebuilt)} TXs)"
            now = time.time()
            fire_time = execute_ts - latency_offset

            # 🔥 LATE GUARD
            if fire_time < now - 0.2:
                gui_log(
                    f"⏭️ {pub_key[:6]}... Missed window "
                    f"({now - fire_time:.3f}s late). Firing immediately.",
                    "warn"
                )
                execute_ts = now + 0.01  # immediate controlled fire
            
            with WALLET_LOCK:
                if pub_key in WALLET_ACTIVE:
                    gui_log(
                        f"⏸️ {pub_key[:6]}... Lifecycle already active, skipping.",
                        "info"
                    )
                    time.sleep(1)
                    continue
                WALLET_ACTIVE.add(pub_key)


            lifecycle_orchestrator(
                execute_ts,
                prebuilt,
                server_pool,
                master_kp,
                fee_pairs,
                dest_addr,
                topup_cfg,
                base_fee,
                pub_key,
                latency_offset
            )


            time.sleep(3)

        except Exception as e:
            gui_log(f"Error {pub_key[:6]}: {e}", "err")
            time.sleep(5)

    RUNNING_TASKS.discard(pub_key)
