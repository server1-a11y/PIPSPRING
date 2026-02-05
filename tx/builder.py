# tx/builder.py
import time
from stellar_sdk import (
    TransactionBuilder,
    Asset,
    TimeBounds
)

from config import NETWORK_PASSPHRASE


def build_tx_params(
    unlock_id,
    amount,
    claimant_kp,
    fee_kp,
    base_fee,
    timeout_sec,
    dest_addr,
    memo_text,
    schedule_ts=None
):
    return {
        "unlock_id": unlock_id,
        "amount": amount,
        "claimant_kp": claimant_kp,
        "fee_kp": fee_kp,
        "base_fee": base_fee,
        "timeout": timeout_sec,
        "dest": dest_addr,
        "memo": memo_text,
        "schedule_ts": schedule_ts
    }


def build_signed_tx(server_pool, params, idx):
    server = server_pool[idx % len(server_pool)]

    try:
        fee_account = server.load_account(
            params["fee_kp"].public_key
        )

        if params["schedule_ts"]:
            tb = TimeBounds(
                0,
                int(params["schedule_ts"] + params["timeout"])
            )
        else:
            tb = TimeBounds(
                0,
                int(time.time() + params["timeout"])
            )

        txb = TransactionBuilder(
            fee_account,
            NETWORK_PASSPHRASE,
            base_fee=params["base_fee"]
        )
        txb.time_bounds = tb

        txb.append_claim_claimable_balance_op(
            balance_id=params["unlock_id"],
            source=params["claimant_kp"].public_key
        )

        txb.append_payment_op(
            destination=params["dest"],
            amount=params["amount"],
            asset=Asset.native(),
            source=params["claimant_kp"].public_key
        )

        if params["memo"]:
            txb.add_text_memo(params["memo"])

        tx = txb.build()
        tx.sign(params["claimant_kp"])
        tx.sign(params["fee_kp"])

        return {
            "tx_obj": tx,
            "target_server_index": idx % len(server_pool),
            "fee_kp": params["fee_kp"].public_key
        }
    except:
        return None
