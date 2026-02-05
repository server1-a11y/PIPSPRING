# automation/topup.py
import concurrent.futures
import threading

from stellar_sdk import TransactionBuilder, Asset, Payment
from state import SEQUENCE_LOCK
from core.utils import gui_log

CRITICAL_THRESHOLD = 0.5

def perform_auto_topup(
    server_pool,
    master_kp,
    fee_kps,
    trigger_threshold,
    topup_amount,
    dynamic_fee,
    pub_key_id,
    is_time_critical=False
):
    if not master_kp:
        return

    unique_fee_kps = list({kp.public_key: kp for kp in fee_kps}.values())
    needy_wallets = []
    lock = threading.Lock()

    def check_balance(kp, idx):
        try:
            srv = server_pool[idx % len(server_pool)]
            acc = srv.accounts().account_id(kp.public_key).call()
            bal = next(
                float(b["balance"])
                for b in acc["balances"]
                if b["asset_type"] == "native"
            )
            if bal < CRITICAL_THRESHOLD or (
                is_time_critical and bal < trigger_threshold
            ):
                with lock:
                    needy_wallets.append(kp)
        except:
            pass

    with concurrent.futures.ThreadPoolExecutor(max_workers=50) as ex:
        for i, kp in enumerate(unique_fee_kps):
            ex.submit(check_balance, kp, i)

    if not needy_wallets:
        return

    gui_log(
        f"💰 {pub_key_id[:6]}... Topup {len(needy_wallets)} wallets",
        "warn"
    )

    ops = [
        Payment(
            destination=kp.public_key,
            amount=str(topup_amount),
            asset=Asset.native()
        )
        for kp in needy_wallets
    ]

    main_server = server_pool[0]
    batch_size = 100

    for i in range(0, len(ops), batch_size):
        chunk = ops[i:i + batch_size]
        with SEQUENCE_LOCK:
            try:
                acc = main_server.load_account(master_kp.public_key)
                txb = TransactionBuilder(
                    acc,
                    network_passphrase="Pi Network",
                    base_fee=dynamic_fee
                )
                for op in chunk:
                    txb.append_operation(op)
                txb.set_timeout(30)
                tx = txb.build()
                tx.sign(master_kp)
                main_server.submit_transaction(tx)
                gui_log(f"Topup Success: {len(chunk)} wallets", "ok")
            except Exception as e:
                gui_log(f"Topup Failed: {str(e)[:60]}", "err")
