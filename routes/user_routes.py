from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from middleware.auth_middleware import admin_required, superadmin_required, login_required
from controllers.user_controller import (
    get_all_users, get_user, create_user, update_user, delete_user,
    promote_to_admin, demote_to_staff
)

user_bp = Blueprint("users", __name__)


@user_bp.route("/users")
@admin_required
def index():
    users = get_all_users()
    current_role = session.get("role")
    visible_users = [u for u in users if u["role"] == "staff"] if current_role == "admin" else users
    return render_template(
        "users.html",
        users=visible_users,
        all_users=users,
        user={"name": session.get("user_name"), "role": current_role},
        current_uid=session.get("user_id"),
    )


@user_bp.route("/users/add", methods=["POST"])
@admin_required
def add():
    name     = request.form.get("name", "").strip()
    email    = request.form.get("email", "").strip()
    password = request.form.get("password", "")
    role     = request.form.get("role", "staff")
    if session.get("role") == "admin":
        role = "staff"
    if not all([name, email, password]):
        flash("All fields are required.", "error")
        return redirect(url_for("users.index"))
    _, error = create_user(name, email, password, role)
    if error:
        flash(error, "error")
    else:
        flash(f"User '{name}' created successfully!", "success")
    return redirect(url_for("users.index"))


@user_bp.route("/users/edit/<int:uid>", methods=["POST"])
@admin_required
def edit(uid):
    name     = request.form.get("name", "").strip()
    email    = request.form.get("email", "").strip()
    role     = request.form.get("role", "staff")
    password = request.form.get("password", "").strip() or None
    if session.get("role") == "admin":
        role = "staff"
    if not all([name, email]):
        flash("Name and email are required.", "error")
        return redirect(url_for("users.index"))
    try:
        update_user(uid, name, email, role, password)
        flash("User updated successfully!", "success")
    except Exception as e:
        flash(f"Error: {e}", "error")
    return redirect(url_for("users.index"))


@user_bp.route("/users/delete/<int:uid>", methods=["POST"])
@admin_required
def delete(uid):
    if uid == session.get("user_id"):
        flash("You cannot delete your own account.", "error")
        return redirect(url_for("users.index"))
    try:
        target = get_user(uid)
        if target and target["role"] in ("admin", "superadmin") and session.get("role") != "superadmin":
            flash("Only superadmin can delete admin accounts.", "error")
            return redirect(url_for("users.index"))
        delete_user(uid)
        flash("User deleted.", "success")
    except Exception as e:
        flash(f"Error: {e}", "error")
    return redirect(url_for("users.index"))


@user_bp.route("/users/promote/<int:uid>", methods=["POST"])
@superadmin_required
def promote(uid):
    try:
        promote_to_admin(uid)
        flash("User promoted to Admin.", "success")
    except Exception as e:
        flash(str(e), "error")
    return redirect(url_for("users.index"))


@user_bp.route("/users/demote/<int:uid>", methods=["POST"])
@superadmin_required
def demote(uid):
    try:
        demote_to_staff(uid)
        flash("Admin demoted to Staff.", "success")
    except Exception as e:
        flash(str(e), "error")
    return redirect(url_for("users.index"))
