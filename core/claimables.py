# core/claimables.py
from datetime import datetime, timezone

def get_claimables_for_claimant(server, claimant_addr):
    try:
        res = (
            server.claimable_balances()
            .for_claimant(claimant_addr)
            .limit(200)
            .call()
        )
        return res.get("_embedded", {}).get("records", [])
    except:
        return []


def choose_claimable(records, claimant_addr):
    now = datetime.now(timezone.utc)
    earliest = None

    for c in records:
        for cl in c.get("claimants", []):
            if cl.get("destination") != claimant_addr:
                continue

            pred = cl.get("predicate", {})
            if pred == {"unconditional": True}:
                return c

            if "not" in pred and "abs_before" in pred["not"]:
                t = datetime.fromisoformat(
                    pred["not"]["abs_before"].replace("Z", "+00:00")
                )
                if earliest is None or t < earliest[0]:
                    earliest = (t, c)

    return earliest[1] if earliest else None


def get_unlock_time(record, claimant_addr):
    for cl in record.get("claimants", []):
        if cl.get("destination") == claimant_addr:
            pred = cl.get("predicate", {})
            if "not" in pred and "abs_before" in pred["not"]:
                return datetime.fromisoformat(
                    pred["not"]["abs_before"].replace("Z", "+00:00")
                )
    return None


def get_asset_code(record):
    asset = record.get("asset", "native")
    if asset == "native":
        # return "XLM/Pi (Native)"
        return "Pi"
    return asset.split(":")[0]
