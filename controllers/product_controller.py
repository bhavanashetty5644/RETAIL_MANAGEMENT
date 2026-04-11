from db import sb_get, sb_post, sb_patch, sb_delete, cache_invalidate

def get_all_products():
    return sb_get("products", {"select": "*", "order": "id.asc"}, use_cache=False)

def get_product(pid):
    rows = sb_get("products", {"id": f"eq.{pid}", "select": "*"}, use_cache=False)
    return rows[0] if rows else None

def add_product(name, price, quantity, category="General"):
    result = sb_post("products", {
        "name":     name.strip(),
        "price":    float(price),
        "quantity": int(quantity),
        "category": category.strip() or "General"
    })
    cache_invalidate("products")
    if not result or not result.get("id"):
        raise RuntimeError("Failed to add product — check service key and RLS policies.")
    return result

def update_product(pid, data):
    allowed = {k: data[k] for k in ("name","price","quantity","category") if k in data}
    result = sb_patch("products", pid, allowed)
    cache_invalidate("products")
    return result

def delete_product(pid):
    result = sb_delete("products", pid)
    cache_invalidate("products")
    return result
