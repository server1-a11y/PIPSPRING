# automation/lifecycle.py
import time
import concurrent.futures
from datetime import datetime

from state import WEB_TASKS
from core.utils import gui_log
from automation.topup import perform_auto_topup
from automation.sweep import perform_auto_sweep

from state import RUNNING_TASKS
import time
from state import WALLET_ACTIVE, WALLET_LOCK

TOPUP_TIME_WINDOW = 180  # keep local copy for now

def lifecycle_orchestrator(
    target_ts,
    prebuilt_txs,
    server_pool,
    master_kp,
    fee_pairs,
    sweep_dest,
    topup_cfg,
    global_fee,
    pub_key_id,
    latency_offset=0.5
):
    last_topup_check = time.time()
    initial_critical_topup_done = False

    curr = WEB_TASKS.get(pub_key_id, {})
    current_asset = curr.get("asset", "N/A")
    current_amount = curr.get("amount", "N/A")
    current_schedule = curr.get("schedule", "N/A")

    fire_time = target_ts - latency_offset

    gui_log(
        f"⏰ {pub_key_id[:6]}... Target: "
        f"{datetime.fromtimestamp(target_ts).strftime('%H:%M:%S.%f')[:-3]}",
        "info"
    )

    # inside lifecycle_orchestrator loop
    while pub_key_id in RUNNING_TASKS:
        now = time.time()
        remaining = fire_time - now

        if remaining <= 0:
            break

        if remaining > 0.1:
            WEB_TASKS[pub_key_id]["status"] = f"Wait: {remaining:.2f}s"

        # critical topup window
        if remaining < TOPUP_TIME_WINDOW and not initial_critical_topup_done:
            gui_log(f"⚡ {pub_key_id[:6]}... Recharge Coins.", "warn")
            perform_auto_topup(
                server_pool,
                master_kp,
                fee_pairs,
                topup_cfg["threshold"],
                topup_cfg["amount"],
                global_fee,
                pub_key_id,
                is_time_critical=True
            )
            initial_critical_topup_done = True

        # SAFE WAIT STRATEGY
        if remaining > 1.5:
            time.sleep(0.2)
        elif remaining > 0.3:
            time.sleep(0.05)
        elif remaining > 0.02:
            time.sleep(0.005)
        else:
            time.sleep(0.001)  # micro-sleep prevents CPU starvation


    WEB_TASKS[pub_key_id]["status"] = "🚀 FIRING!!!"
    gui_log(
        f"🚀 {pub_key_id[:6]}... SHOOTING {len(prebuilt_txs)} TXs!",
        "warn"
    )

    results = []
    max_workers = min(len(prebuilt_txs), 1500)

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as ex:
        futures = []
        for p in prebuilt_txs:
            srv = server_pool[p["target_server_index"]]
            futures.append(
                ex.submit(
                    srv.submit_transaction,
                    p["tx_obj"]
                )
            )

        for f in concurrent.futures.as_completed(futures, timeout=1.5):
            try:
                f.result()
                results.append(True)
            except Exception:
                results.append(False)

    success_count = sum(results)

    if success_count > 0:
        gui_log(
            f"✅ {pub_key_id[:6]}... Success! "
            f"{success_count}/{len(prebuilt_txs)} txs.",
            "ok"
        )
        WEB_TASKS[pub_key_id]["status"] = "Claim Success"
    else:
        gui_log(
            f"❌ {pub_key_id[:6]}... Failed.",
            "err"
        )
        WEB_TASKS[pub_key_id]["status"] = "Failed"

    time.sleep(1)
    perform_auto_sweep(
        server_pool,
        fee_pairs,
        sweep_dest,
        master_kp,
        global_fee,
        pub_key_id
    )

    with WALLET_LOCK:
        WALLET_ACTIVE.discard(pub_key_id)

