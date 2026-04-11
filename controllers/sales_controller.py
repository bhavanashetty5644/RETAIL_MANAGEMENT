import datetime
import random
from db import sb_get, sb_post, sb_patch, cache_invalidate

def _gen_invoice():
    return f"INV-{datetime.date.today().strftime('%Y%m%d')}-{random.randint(1000,9999)}"

def get_all_sales():
    return sb_get("sales", {"order": "id.desc"}, use_cache=False)

def get_sale(sid):
    rows = sb_get("sales", {"id": f"eq.{sid}"}, use_cache=False)
    if not rows:
        return None
    sale = rows[0]
    items = sb_get("sale_items", {"sale_id": f"eq.{sid}", "select": "*"}, use_cache=False)
    sale["items"] = items
    return sale

def create_sale(form_data, items):
    """
    form_data: dict with customer info, discount, tax, payment_mode etc.
    items: list of {"product_id": int, "quantity": int, "unit_price": float}
    """
    if not items:
        return None, "At least one item is required"

    customer_name  = form_data.get("customer_name", "").strip()
    if not customer_name:
        return None, "Customer name is required"

    # Verify stock and compute subtotal
    subtotal = 0.0
    enriched_items = []
    for it in items:
        pid   = int(it["product_id"])
        qty   = int(it["quantity"])
        price = float(it["unit_price"])
        # fetch product
        prods = sb_get("products", {"id": f"eq.{pid}", "select": "*"}, use_cache=False)
        if not prods:
            return None, f"Product ID {pid} not found"
        p = prods[0]
        if int(p.get("quantity", 0)) < qty:
            return None, f"Insufficient stock for '{p['name']}'. Available: {p['quantity']}"
        line_total = round(qty * price, 2)
        subtotal  += line_total
        enriched_items.append({"product_id": pid, "product_name": p["name"],
                                "quantity": qty, "unit_price": price, "total_price": line_total,
                                "_stock": int(p["quantity"])})

    discount = round(float(form_data.get("discount", 0)), 2)
    tax_pct  = round(float(form_data.get("tax_pct", 18)), 2)
    taxable  = round(subtotal - discount, 2)
    tax_amt  = round(taxable * tax_pct / 100, 2)
    total    = round(taxable + tax_amt, 2)

    invoice_no = _gen_invoice()
    sale = sb_post("sales", {
        "invoice_no":        invoice_no,
        "customer_name":     customer_name,
        "customer_phone":    form_data.get("customer_phone", ""),
        "customer_email":    form_data.get("customer_email", ""),
        "customer_address":  form_data.get("customer_address", ""),
        "subtotal":          round(subtotal, 2),
        "discount":          discount,
        "tax":               tax_amt,
        "total":             total,
        "payment_mode":      form_data.get("payment_mode", "cash"),
        "status":            "paid",
        "notes":             form_data.get("notes", ""),
    })

    sale_id = sale["id"]

    # Insert line items & deduct stock
    for it in enriched_items:
        sb_post("sale_items", {
            "sale_id":      sale_id,
            "product_id":   it["product_id"],
            "product_name": it["product_name"],
            "quantity":     it["quantity"],
            "unit_price":   it["unit_price"],
            "total_price":  it["total_price"],
        })
        new_qty = it["_stock"] - it["quantity"]
        sb_patch("products", it["product_id"], {"quantity": new_qty})
        cache_invalidate("products")

    sale["items"] = enriched_items
    return sale, None

def get_sales_stats():
    try:
        rows = sb_get("sales", {"select": "status,total,total_price,total_amount,created_at"}, use_cache=False)
    except Exception:
        return {
            "total_sales": 0, "total_revenue": 0, "today_count": 0, "today_revenue": 0
        }

    # Normalize rows for stats calculation
    for r in rows:
        if 'total' not in r:
            r['total'] = r.get('total_price') or r.get('total_amount') or 0

    paid = [r for r in rows if r.get("status") in ("paid", "completed", None)] # default to paid if status missing
    today = datetime.date.today().isoformat()
    today_sales = [r for r in paid if r.get("created_at") and r["created_at"].startswith(today)]

    return {
        "total_sales":   len(rows),
        "total_revenue": round(sum(float(r.get("total", 0)) for r in paid), 2),
        "today_count":   len(today_sales),
        "today_revenue": round(sum(float(r.get("total", 0)) for r in today_sales), 2),
    }
