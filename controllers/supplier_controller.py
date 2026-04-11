from db import sb_get, sb_post, sb_patch, sb_delete

def get_all_suppliers():
    # Must include select=* when passing other params — Supabase requires it
    return sb_get("suppliers", {"select": "*", "order": "id.asc"}, use_cache=False)

def get_supplier(sid):
    rows = sb_get("suppliers", {"id": f"eq.{sid}", "select": "*"}, use_cache=False)
    return rows[0] if rows else None

def create_supplier(data):
    if not data.get("name", "").strip():
        return None, "Supplier name is required"
    # Remove empty string fields so Supabase uses column defaults instead of rejecting
    clean = {k: v for k, v in data.items() if v != "" and v is not None}
    try:
        result = sb_post("suppliers", clean)
        return result, None
    except Exception as e:
        return None, str(e)

def update_supplier(sid, data):
    # Keep empty strings as None so Supabase stores NULL instead of rejecting
    clean = {k: (v if v != "" else None) for k, v in data.items()}
    return sb_patch("suppliers", sid, clean)

def delete_supplier(sid):
    return sb_delete("suppliers", sid)
