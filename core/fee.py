# core/fee.py

def get_network_base_fee(server):
    try:
        stats = server.fee_stats()
        p99 = int(stats["fee_charged"]["p99"])
        fee = int(p99 * 2.0)

        if fee < 500_000:
            fee = 500_000
        if fee > 26_000_000:
            fee = 26_000_000
        return fee
    except:
        return 500_000
