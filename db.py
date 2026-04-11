import os, time
import requests as _req
from dotenv import load_dotenv
load_dotenv()

SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
# Always use service-role key — it bypasses RLS for all operations
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_KEY") or os.environ.get("SUPABASE_KEY", "")

# ── In-memory cache ─────────────────────────────────────────────────────────
_cache: dict = {}
_CACHE_TTL   = 60

def _ck(table, params):
    return f"{table}:{sorted((params or {}).items())}"

def _cget(key):
    e = _cache.get(key)
    return e["data"] if e and (time.time() - e["ts"]) < _CACHE_TTL else None

def _cset(key, data):
    _cache[key] = {"data": data, "ts": time.time()}

def cache_invalidate(table):
    for k in list(_cache.keys()):
        if k.startswith(f"{table}:"):
            del _cache[k]

def _H():
    return {
        "apikey":        SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type":  "application/json",
        "Prefer":        "return=representation",
    }

def _raise_supabase_error(r):
    """Raise a readable RuntimeError from a Supabase error response."""
    try:
        body = r.json()
        msg  = body.get("message") or body.get("error") or body.get("hint") or str(body)
    except Exception:
        msg = r.text or f"HTTP {r.status_code}"
    raise RuntimeError(f"Supabase error {r.status_code}: {msg}")

def sb_get(table, params=None, use_cache=True):
    ck = _ck(table, params)
    if use_cache:
        cached = _cget(ck)
        if cached is not None:
            return cached
    r = _req.get(f"{SUPABASE_URL}/rest/v1/{table}", headers=_H(), params=params, timeout=12)
    if not r.ok:
        _raise_supabase_error(r)
    data = r.json()
    if use_cache:
        _cset(ck, data)
    return data

def sb_post(table, data):
    cache_invalidate(table)
    r = _req.post(f"{SUPABASE_URL}/rest/v1/{table}", headers=_H(), json=data, timeout=12)
    if not r.ok:
        _raise_supabase_error(r)
    res = r.json()
    return res[0] if isinstance(res, list) and res else (res or data)

def sb_patch(table, row_id, data, id_col="id"):
    cache_invalidate(table)
    r = _req.patch(f"{SUPABASE_URL}/rest/v1/{table}", headers=_H(), json=data,
                   params={id_col: f"eq.{row_id}"}, timeout=12)
    if not r.ok:
        _raise_supabase_error(r)
    res = r.json()
    return res[0] if isinstance(res, list) and res else (res or data)

def sb_delete(table, row_id, id_col="id"):
    cache_invalidate(table)
    r = _req.delete(f"{SUPABASE_URL}/rest/v1/{table}", headers=_H(),
                    params={id_col: f"eq.{row_id}"}, timeout=12)
    if not r.ok:
        _raise_supabase_error(r)
    return {"deleted": row_id}
