"""Full transaction history of an account (FastNEAR tx API), with details, cached."""
from .net import tx_account, tx_details, near


def account_hashes(account):
    out, resume = [], None
    while True:
        r = tx_account(account, 200, resume)
        out += r.get("account_txs", [])
        resume = r.get("resume_token")
        if not resume or not r.get("account_txs"):
            break
    return out


def account_history(account):
    """Return the account's transactions in chain order, each summarised."""
    rows = account_hashes(account)
    det = {t["transaction"]["hash"]: t for t in tx_details([r["transaction_hash"] for r in rows])}
    out = []
    for r in rows:
        t = det.get(r["transaction_hash"])
        if t:
            out.append(summarise(t))
    out.sort(key=lambda x: (x["height"], x["hash"]))
    return out


def summarise(t):
    tx = t["transaction"]
    eo = t.get("execution_outcome", {})
    acts = []
    for a in tx["actions"]:
        if isinstance(a, dict) and "Transfer" in a:
            acts.append({"kind": "Transfer", "near": near(a["Transfer"]["deposit"])})
        elif isinstance(a, dict) and "FunctionCall" in a:
            fc = a["FunctionCall"]
            acts.append({"kind": "FunctionCall", "method": fc["method_name"], "near": near(fc.get("deposit", "0"))})
        else:
            acts.append({"kind": a if isinstance(a, str) else next(iter(a))})
    # native NEAR moved by receipts (e.g. a staking pool paying out withdraw_all)
    rec_transfers, logs, ok = [], [], True
    for rc in t.get("receipts", []):
        rr = rc.get("receipt", {})
        body = rr.get("receipt", {}).get("Action", {})
        for a in body.get("actions", []):
            if isinstance(a, dict) and "Transfer" in a and rr.get("predecessor_id") != "system":
                rec_transfers.append({"from": rr.get("predecessor_id"), "to": rr.get("receiver_id"),
                                      "near": near(a["Transfer"]["deposit"])})
        out = rc.get("execution_outcome", {}).get("outcome", {})
        logs += out.get("logs", [])
        if "Failure" in out.get("status", {}):
            ok = False
    return {"hash": tx["hash"], "signer": tx["signer_id"], "receiver": tx["receiver_id"], "actions": acts,
            "height": eo.get("block_height"), "ts": eo.get("block_timestamp"),
            "receipt_transfers": rec_transfers, "logs": logs, "ok": ok}
