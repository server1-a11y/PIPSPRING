# automation/sweep.py
import concurrent.futures
import threading

from stellar_sdk import TransactionBuilder, Asset, Payment
from state import SEQUENCE_LOCK
from core.utils import gui_log

def perform_auto_sweep(
    server_pool,
    fee_kps,
    dest_addr,
    master_kp,
    dynamic_fee,
    pub_key_id
):
    if not dest_addr or not master_kp:
        return

    ops = []
    signers = []
    lock = threading.Lock()

    def scan(kp, idx):
        try:
            srv = server_pool[idx % len(server_pool)]
            acc = srv.accounts().account_id(kp.public_key).call()
            bal = next(
                float(b["balance"])
                for b in acc["balances"]
                if b["asset_type"] == "native"
            )
            sweep_amt = bal - 0.98
            if sweep_amt > 0.01 and kp.public_key != dest_addr:
                with lock:
                    ops.append(
                        Payment(
                            destination=dest_addr,
                            amount=f"{sweep_amt:.6f}",
                            asset=Asset.native(),
                            source=kp.public_key
                        )
                    )
                    signers.append(kp)
        except:
            pass

    with concurrent.futures.ThreadPoolExecutor(max_workers=100) as ex:
        for i, kp in enumerate({k.public_key: k for k in fee_kps}.values()):
            ex.submit(scan, kp, i)

    if not ops:
        return

    gui_log(f"🧹 Sweeping {len(ops)} wallets...", "info")

    main_server = server_pool[0]
    batch_size = 19

    for i in range(0, len(ops), batch_size):
        with SEQUENCE_LOCK:
            try:
                acc = main_server.load_account(master_kp.public_key)
                txb = TransactionBuilder(
                    acc,
                    network_passphrase="Pi Network",
                    base_fee=dynamic_fee
                )
                for op in ops[i:i + batch_size]:
                    txb.append_operation(op)
                txb.set_timeout(30)
                tx = txb.build()
                tx.sign(master_kp)
                for kp in signers[i:i + batch_size]:
                    tx.sign(kp)
                main_server.submit_transaction(tx)
                gui_log("✅ Sweep batch success", "ok")
            except Exception as e:
                gui_log(f"❌ Sweep error: {str(e)[:60]}", "err")
