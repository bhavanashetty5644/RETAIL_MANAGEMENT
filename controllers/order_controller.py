from db import sb_get, sb_post, sb_patch, sb_delete, cache_invalidate

def get_all_orders():
    return sb_get("orders", {
        "select": "id,quantity,total_price,created_at,products(id,name,price,category)",
        "order": "id.desc"
    }, use_cache=False)

def get_order(oid):
    rows = sb_get("orders", {
        "id": f"eq.{oid}",
        "select": "id,quantity,total_price,created_at,products(id,name,price,category)"
    }, use_cache=False)
    return rows[0] if rows else None

def create_order(product_id, quantity):
    products = sb_get("products", {"id": f"eq.{product_id}", "select": "*"}, use_cache=False)
    if not products:
        return None, "Product not found"
    product = products[0]
    qty = int(quantity)
    if product["quantity"] < qty:
        return None, f"Insufficient stock. Available: {product['quantity']}"
    total_price = round(float(product["price"]) * qty, 2)
    order = sb_post("orders", {
        "product_id":  int(product_id),
        "quantity":    qty,
        "total_price": total_price
    })
    sb_patch("products", product_id, {"quantity": product["quantity"] - qty})
    cache_invalidate("products")
    return order, None

def delete_order(oid):
    order = get_order(oid)
    if order:
        prod = order.get("products") or {}
        if isinstance(prod, list): prod = prod[0] if prod else {}
        if prod.get("id"):
            prods = sb_get("products", {"id": f"eq.{prod['id']}", "select": "quantity"}, use_cache=False)
            if prods:
                sb_patch("products", prod["id"], {"quantity": prods[0]["quantity"] + order["quantity"]})
                cache_invalidate("products")
    return sb_delete("orders", oid)

def get_sales_summary():
    orders = sb_get("orders", {"select": "total_price"}, use_cache=False)
    return {
        "total_revenue": round(sum(float(o.get("total_price", 0)) for o in orders), 2),
        "total_orders":  len(orders)
    }

def get_orders_csv():
    orders = get_all_orders()
    lines = ["Order ID,Product,Category,Qty,Unit Price,Total,Date"]
    for o in orders:
        prod = o.get("products") or {}
        if isinstance(prod, list): prod = prod[0] if prod else {}
        lines.append(
            f'{o["id"]},"{prod.get("name","N/A")}","{prod.get("category","General")}",'
            f'{o["quantity"]},{prod.get("price",0)},{o["total_price"]},'
            f'{str(o.get("created_at",""))[:10]}'
        )
    return "\n".join(lines)
