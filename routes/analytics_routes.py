from flask import Blueprint, render_template, jsonify, session
from middleware.auth_middleware import login_required
from controllers.order_controller import get_all_orders
from controllers.product_controller import get_all_products
from collections import defaultdict

reports_analytics_bp = Blueprint("analytics", __name__)


def _build_analytics():
    orders = get_all_orders()
    products = get_all_products()

    # Revenue by day (last 30 orders)
    daily = defaultdict(float)
    category_revenue = defaultdict(float)
    product_revenue = defaultdict(float)

    for o in orders:
        date = str(o.get("created_at", ""))[:10]
        total = float(o.get("total_price", 0))
        daily[date] += total

        prod = o.get("products") or {}
        if isinstance(prod, list):
            prod = prod[0] if prod else {}
        cat = prod.get("category", "General")
        pname = prod.get("name", "Unknown")
        category_revenue[cat] += total
        product_revenue[pname] += total

    sorted_daily = sorted(daily.items())[-30:]

    # Category stock levels
    cat_stock = defaultdict(int)
    for p in products:
        cat_stock[p.get("category", "General")] += p.get("quantity", 0)

    top_products = sorted(product_revenue.items(), key=lambda x: x[1], reverse=True)[:5]

    return {
        "daily_labels": [d[0] for d in sorted_daily],
        "daily_values": [round(d[1], 2) for d in sorted_daily],
        "category_labels": list(category_revenue.keys()),
        "category_values": [round(v, 2) for v in category_revenue.values()],
        "cat_stock_labels": list(cat_stock.keys()),
        "cat_stock_values": list(cat_stock.values()),
        "top_product_labels": [t[0] for t in top_products],
        "top_product_values": [round(t[1], 2) for t in top_products],
        "total_revenue": round(sum(float(o.get("total_price", 0)) for o in orders), 2),
        "total_orders": len(orders),
        "total_products": len(products),
        "low_stock": len([p for p in products if p.get("quantity", 0) <= 5]),
    }


@reports_analytics_bp.route("/reports")
@login_required
def index():
    try:
        data = _build_analytics()
    except Exception as e:
        data = {}
    return render_template(
        "reports.html",
        data=data,
        user={"name": session.get("user_name"), "role": session.get("role")},
    )


@reports_analytics_bp.route("/api/analytics")
@login_required
def api_analytics():
    try:
        return jsonify(_build_analytics())
    except Exception as e:
        return jsonify({"error": str(e)}), 500
