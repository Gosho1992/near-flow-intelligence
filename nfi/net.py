"""Cached, rate-limited access to NEAR's public archival RPC and FastNEAR's transaction API.

Every response is stored gzipped under data/raw/ keyed by a hash of the request, so `make data`
rebuilds everything offline. Set NFI_OFFLINE=1 to forbid network access (used by tests/CI).
"""
import base64, gzip, hashlib, json, os, time, urllib.request, urllib.error
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
RPC_URL = os.environ.get("NFI_RPC", "https://archival-rpc.mainnet.fastnear.com")
TX_URL = "https://tx.main.fastnear.com/v0"
OFFLINE = os.environ.get("NFI_OFFLINE") == "1"
_last = {"rpc": 0.0, "tx": 0.0}
_GAP = {"rpc": 0.08, "tx": 11.0}   # FastNEAR tx API rate-limits hard; RPC is lenient


class OfflineMiss(RuntimeError):
    pass


def _key(kind, body):
    h = hashlib.sha256(json.dumps(body, sort_keys=True).encode()).hexdigest()[:24]
    return RAW / kind / h[:2] / f"{h}.json.gz"


def _post(kind, url, body, cacheable=True, force=False):
    """force=True re-fetches and overwrites a cached answer (used for the last page of a growing history)."""
    path = _key(kind, body)
    if force and OFFLINE:
        force = False
    if cacheable and path.exists() and not force:
        return json.loads(gzip.decompress(path.read_bytes()))["response"]
    if OFFLINE:
        raise OfflineMiss(f"not in cache: {kind} {json.dumps(body)[:160]}")
    for attempt in range(8):
        wait = _GAP[kind] - (time.time() - _last[kind])
        if wait > 0:
            time.sleep(wait)
        _last[kind] = time.time()
        try:
            req = urllib.request.Request(url, data=json.dumps(body).encode(),
                                         headers={"content-type": "application/json"})
            resp = json.load(urllib.request.urlopen(req, timeout=60))
            break
        except urllib.error.HTTPError as e:
            if e.code in (400, 404, 422):          # definitive answer (e.g. no block at this height)
                try:
                    resp = json.loads(e.read().decode())
                except Exception:
                    resp = {"error": {"http": e.code}}
                break
            time.sleep(min(90, 5 * 2 ** attempt))
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, ConnectionError):
            time.sleep(min(90, 5 * 2 ** attempt))
    else:
        raise RuntimeError(f"network failed: {kind} {json.dumps(body)[:160]}")
    if cacheable:
        path.parent.mkdir(parents=True, exist_ok=True)
        # mtime=0 keeps the gzip bytes identical across re-fetches of the same answer
        path.write_bytes(gzip.compress(json.dumps({"request": body, "response": resp}, sort_keys=True).encode(), mtime=0))
    return resp


def rpc(method, params, cacheable=True):
    r = _post("rpc", RPC_URL, {"jsonrpc": "2.0", "id": "nfi", "method": method, "params": params}, cacheable)
    return r


def view(account, method, args, height):
    """Call a contract view method at a block height. Returns decoded JSON or None if the call failed."""
    r = rpc("query", {"request_type": "call_function", "block_id": height, "account_id": account,
                      "method_name": method, "args_base64": base64.b64encode(json.dumps(args).encode()).decode()})
    res = r.get("result")
    if not res or "result" not in res:
        return None
    return json.loads(bytes(res["result"]).decode())


def _unknown_account(r):
    cause = ((r or {}).get("error") or {}).get("cause") or {}
    return cause.get("name") == "UNKNOWN_ACCOUNT"


def account_state(account, height):
    """view_account result dict; {"amount": "0", "locked": "0"} if the account did not exist yet at that
    height (a true zero); None if the lookup failed or returned something else (missing, never zero)."""
    r = rpc("query", {"request_type": "view_account", "block_id": height, "account_id": account})
    if _unknown_account(r):
        return {"amount": "0", "locked": "0", "status": "not_created"}
    res = r.get("result")
    if not res or "amount" not in res or "locked" not in res:
        return None
    return {**res, "status": "observed"}


def view_account(account, height):
    """Liquid balance in yoctoNEAR: 0 if the account did not exist yet; None if the lookup failed."""
    st = account_state(account, height)
    return None if st is None else int(st["amount"])


def block(height):
    r = rpc("block", {"block_id": height})
    return r.get("result", {}).get("header")


def tx_account(account, limit=200, resume=None, force=False):
    body = {"account_id": account, "limit": limit, "desc": False}
    if resume:
        body["resume_token"] = resume
    return _post("tx", TX_URL + "/account", body, force=force)


def tx_details(hashes):
    out = []
    for i in range(0, len(hashes), 20):
        out += _post("tx", TX_URL + "/transactions", {"tx_hashes": sorted(hashes[i:i + 20])}).get("transactions", [])
    return out


YOCTO = 10 ** 24


def near(yocto):
    return int(yocto) / YOCTO
