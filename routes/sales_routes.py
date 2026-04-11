import json
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from middleware.auth_middleware import login_required
from controllers.sales_controller import get_all_sales, get_sale, create_sale, get_sales_stats
from controllers.product_controller import get_all_products

sales_bp = Blueprint("sales", __name__)

@sales_bp.route("/sales")
@login_required
def index():
    try:
        all_sales = get_all_sales()
        stats     = get_sales_stats()
        products  = get_all_products()
    except Exception as e:
        flash(f"Database sync issue: {e}", "error")
        all_sales, stats, products = [], {"total_sales":0,"total_revenue":0,"today_count":0,"today_revenue":0}, []

    return render_template("sales.html", sales=all_sales, stats=stats, products=products,
                           user={"name": session.get("user_name"), "role": session.get("role")})

@sales_bp.route("/sales/create", methods=["POST"])
@login_required
def create():
    # Parse items JSON from hidden field
    try:
        items = json.loads(request.form.get("items_json", "[]"))
    except Exception:
        flash("Invalid items data.", "error")
        return redirect(url_for("sales.index"))

    sale, error = create_sale(request.form, items)
    if error:
        flash(error, "error")
        return redirect(url_for("sales.index"))

    flash(f"Sale {sale.get('invoice_no')} created! Total: ₹{sale.get('total')}", "success")
    return redirect(url_for("sales.invoice", sid=sale["id"]))

@sales_bp.route("/sales/<int:sid>/invoice")
@login_required
def invoice(sid):
    sale = get_sale(sid)
    if not sale:
        flash("Sale not found.", "error")
        return redirect(url_for("sales.index"))
    return render_template("sales_invoice.html", sale=sale,
                           user={"name": session.get("user_name"), "role": session.get("role")})

@sales_bp.route("/api/sales/<int:sid>")
@login_required
def api_get(sid):
    sale = get_sale(sid)
    if not sale:
        return jsonify({"error": "Not found"}), 404
    return jsonify(sale)
