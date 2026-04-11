from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, session
from middleware.auth_middleware import login_required, admin_required
from controllers.product_controller import get_all_products, add_product, update_product, delete_product

product_bp = Blueprint("products", __name__)

@product_bp.route("/products")
@login_required
def index():
    products = get_all_products()
    return render_template("products.html", products=products,
                           user={"name":session.get("user_name"), "role":session.get("role")})

@product_bp.route("/products/add", methods=["POST"])
@login_required
def add():
    name     = request.form.get("name","").strip()
    price    = request.form.get("price")
    quantity = request.form.get("quantity")
    category = request.form.get("category","General").strip()
    if not all([name, price, quantity]):
        flash("All fields are required.", "error")
        return redirect(url_for("products.index"))
    try:
        add_product(name, float(price), int(quantity), category)
        flash(f"Product '{name}' added successfully!", "success")
    except Exception as e:
        flash(f"Error: {e}", "error")
    return redirect(url_for("products.index"))

@product_bp.route("/products/edit/<int:pid>", methods=["POST"])
@login_required
def edit(pid):
    data = {k: request.form[k] for k in ("name","price","quantity","category") if request.form.get(k)}
    if "price" in data:    data["price"]    = float(data["price"])
    if "quantity" in data: data["quantity"] = int(data["quantity"])
    try:
        update_product(pid, data)
        flash("Product updated successfully!", "success")
    except Exception as e:
        flash(f"Error: {e}", "error")
    return redirect(url_for("products.index"))

@product_bp.route("/products/delete/<int:pid>", methods=["POST"])
@admin_required
def delete(pid):
    try:
        delete_product(pid)
        flash("Product deleted.", "success")
    except Exception as e:
        flash(f"Error: {e}", "error")
    return redirect(url_for("products.index"))

# JSON API
@product_bp.route("/api/products")
@login_required
def api_list():
    return jsonify(get_all_products())
