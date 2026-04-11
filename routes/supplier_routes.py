from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from middleware.auth_middleware import login_required, admin_required
from controllers.supplier_controller import (
    get_all_suppliers, get_supplier, create_supplier, update_supplier, delete_supplier
)

supplier_bp = Blueprint("suppliers", __name__)

@supplier_bp.route("/suppliers")
@login_required
def index():
    suppliers = get_all_suppliers()
    return render_template("suppliers.html", suppliers=suppliers,
                           user={"name": session.get("user_name"), "role": session.get("role")})

@supplier_bp.route("/suppliers/create", methods=["POST"])
@admin_required
def create():
    data = {
        "name":         request.form.get("name", "").strip(),
        "contact_name": request.form.get("contact_name", "").strip(),
        "email":        request.form.get("email", "").strip(),
        "phone":        request.form.get("phone", "").strip(),
        "address":      request.form.get("address", "").strip(),
        "gstin":        request.form.get("gstin", "").strip(),
        "category":     request.form.get("category", "General").strip(),
        "status":       "active",
    }
    supplier, error = create_supplier(data)
    if error:
        flash(error, "error")
    else:
        flash(f"Supplier '{supplier['name']}' added successfully!", "success")
    return redirect(url_for("suppliers.index"))

@supplier_bp.route("/suppliers/<int:sid>/edit", methods=["POST"])
@admin_required
def edit(sid):
    data = {
        "name":         request.form.get("name", "").strip(),
        "contact_name": request.form.get("contact_name", "").strip(),
        "email":        request.form.get("email", "").strip(),
        "phone":        request.form.get("phone", "").strip(),
        "address":      request.form.get("address", "").strip(),
        "gstin":        request.form.get("gstin", "").strip(),
        "category":     request.form.get("category", "General").strip(),
        "status":       request.form.get("status", "active"),
    }
    update_supplier(sid, data)
    flash("Supplier updated.", "success")
    return redirect(url_for("suppliers.index"))

@supplier_bp.route("/suppliers/<int:sid>/delete", methods=["POST"])
@admin_required
def delete(sid):
    delete_supplier(sid)
    flash("Supplier removed.", "success")
    return redirect(url_for("suppliers.index"))
