from db import sb_get, sb_post, sb_patch, cache_invalidate
from controllers.product_controller import get_all_products

def get_all_procurement():
    return sb_get("procurement", {
        "select": "id,quantity,unit_cost,total_cost,status,po_number,notes,created_at,received_at,suppliers(id,name),products(id,name,category)",
        "order":  "id.desc"
    }, use_cache=False)

def get_procurement(pid):
    rows = sb_get("procurement", {
        "id":     f"eq.{pid}",
        "select": "id,quantity,unit_cost,total_cost,status,po_number,notes,created_at,received_at,suppliers(id,name),products(id,name,category)"
    }, use_cache=False)
    return rows[0] if rows else None

def create_procurement(data):
    supplier_id = data.get("supplier_id")
    product_id  = data.get("product_id")
    quantity    = int(data.get("quantity", 0))
    unit_cost   = float(data.get("unit_cost", 0))
    if not supplier_id or not product_id or quantity <= 0 or unit_cost <= 0:
        return None, "Supplier, product, quantity and unit cost are required"
    total_cost  = round(quantity * unit_cost, 2)
    import random, datetime
    po_number   = data.get("po_number") or f"PO-{datetime.date.today().strftime('%Y%m%d')}-{random.randint(1000,9999)}"
    record      = sb_post("procurement", {
        "supplier_id": int(supplier_id),
        "product_id":  int(product_id),
        "quantity":    quantity,
        "unit_cost":   unit_cost,
        "total_cost":  total_cost,
        "status":      data.get("status", "pending"),
        "po_number":   po_number,
        "notes":       data.get("notes", "")
    })
    return record, None

def receive_procurement(pid):
    """Mark procurement as received and add stock to product."""
    po = get_procurement(pid)
    if not po:
        return None, "Purchase order not found"
    if po.get("status") == "received":
        return None, "Already received"
    # Update stock
    products = sb_get("products", {"id": f"eq.{po['product_id']}", "select": "*"}, use_cache=False)
    if products:
        p = products[0]
        new_qty = int(p.get("quantity", 0)) + int(po["quantity"])
        sb_patch("products", po["product_id"], {"quantity": new_qty})
        cache_invalidate("products")
    import datetime
    updated = sb_patch("procurement", pid, {
        "status":      "received",
        "received_at": datetime.datetime.utcnow().isoformat()
    })
    return updated, None

def cancel_procurement(pid):
    updated = sb_patch("procurement", pid, {"status": "cancelled"})
    return updated, None

def get_procurement_stats():
    try:
        rows = sb_get("procurement", {"select": "status,total_cost"}, use_cache=False)
    except Exception:
        return {
            "total_pos": 0, "total_cost": 0, "pending_count": 0,
            "received_count": 0, "cancelled_count": 0, "pending_value": 0
        }

    total_cost   = sum(float(r.get("total_cost", 0)) for r in rows)
    pending      = [r for r in rows if r.get("status") == "pending"]
    received     = [r for r in rows if r.get("status") == "received"]
    cancelled    = [r for r in rows if r.get("status") == "cancelled"]
    return {
        "total_pos":       len(rows),
        "total_cost":      round(total_cost, 2),
        "pending_count":   len(pending),
        "received_count":  len(received),
        "cancelled_count": len(cancelled),
        "pending_value":   round(sum(float(r.get("total_cost",0)) for r in pending), 2),
    }
