# tx/submitter.py

def submit_fast_worker(server, tx_obj, fee_kp_pub):
    try:
        res = server.submit_transaction(tx_obj)
        return {
            "success": True,
            "hash": res.get("hash"),
            "fee_payer": fee_kp_pub
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "fee_payer": fee_kp_pub
        }
