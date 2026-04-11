from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, session
from middleware.auth_middleware import login_required
from controllers.order_controller import get_all_orders, get_order, create_order
from controllers.product_controller import get_all_products

order_bp = Blueprint("orders", __name__)

# Cache products in module-level variable to avoid double DB hit on orders page
_products_cache = None

@order_bp.route("/orders")
@login_required
def index():
    try:
        # Fetch orders and products — both are cached so second call is instant
        orders   = get_all_orders()
        products = get_all_products()
    except Exception as e:
        from flask import flash
        flash(f"Database sync issue: {e}", "error")
        orders, products = [], []

    return render_template("orders.html", orders=orders, products=products,
                           user={"name": session.get("user_name"), "role": session.get("role")})

@order_bp.route("/orders/create", methods=["POST"])
@login_required
def create():
    product_id = request.form.get("product_id")
    quantity   = request.form.get("quantity")
    if not product_id or not quantity:
        flash("Product and quantity are required.", "error")
        return redirect(url_for("orders.index"))
    try:
        order, error = create_order(int(product_id), int(quantity))
        if error:
            flash(error, "error")
        else:
            flash(f"Order #{order['id']} created successfully!", "success")
    except Exception as e:
        flash(f"Error: {e}", "error")
    return redirect(url_for("orders.index"))

@order_bp.route("/invoice/<int:oid>")
@login_required
def invoice(oid):
    order = get_order(oid)
    if not order:
        flash("Order not found.", "error")
        return redirect(url_for("orders.index"))
    return render_template("sales_invoice.html", order=order,
                           user={"name": session.get("user_name"), "role": session.get("role")})
