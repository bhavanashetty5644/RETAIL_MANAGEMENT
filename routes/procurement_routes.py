from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from middleware.auth_middleware import login_required, admin_required
from controllers.procurement_controller import (
    get_all_procurement, create_procurement, receive_procurement, cancel_procurement, get_procurement_stats
)
from controllers.supplier_controller import get_all_suppliers
from controllers.product_controller import get_all_products

procurement_bp = Blueprint("procurement", __name__)

@procurement_bp.route("/procurement")
@login_required
def index():
    try:
        pos       = get_all_procurement()
        stats     = get_procurement_stats()
        suppliers = get_all_suppliers()
        products  = get_all_products()
    except Exception as e:
        flash(f"Database sync issue: {e}", "error")
        pos, stats, suppliers, products = [], {"total_pos":0,"total_cost":0,"pending_count":0,"received_count":0,"cancelled_count":0,"pending_value":0}, [], []

    return render_template("procurement.html", pos=pos, stats=stats,
                           suppliers=suppliers, products=products,
                           user={"name": session.get("user_name"), "role": session.get("role")})

@procurement_bp.route("/procurement/create", methods=["POST"])
@admin_required
def create():
    result, error = create_procurement(request.form)
    if error:
        flash(error, "error")
    else:
        flash(f"Purchase Order {result.get('po_number','#')} created!", "success")
    return redirect(url_for("procurement.index"))

@procurement_bp.route("/procurement/<int:pid>/receive", methods=["POST"])
@admin_required
def receive(pid):
    result, error = receive_procurement(pid)
    if error:
        flash(error, "error")
    else:
        flash("Stock updated — Purchase Order marked as received.", "success")
    return redirect(url_for("procurement.index"))

@procurement_bp.route("/procurement/<int:pid>/cancel", methods=["POST"])
@admin_required
def cancel(pid):
    cancel_procurement(pid)
    flash("Purchase Order cancelled.", "success")
    return redirect(url_for("procurement.index"))
