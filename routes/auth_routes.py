import secrets, datetime
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from controllers.auth_controller import login_user, register_user

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/", methods=["GET"])
@auth_bp.route("/login", methods=["GET"])
def login_page():
    if session.get("user_id") and session.get("_st"):
        return redirect(url_for("dashboard.index"))
    return render_template("login.html")

@auth_bp.route("/login", methods=["POST"])
def login():
    email    = request.form.get("email", "").strip()
    password = request.form.get("password", "")
    if not email or not password:
        flash("Email and password are required.", "error")
        return render_template("login.html")
    user, error = login_user(email, password)
    if error:
        flash(error, "error")
        return render_template("login.html")
    # Clear any old session first, then create fresh one
    session.clear()
    session.permanent = True
    session["user_id"]    = user["id"]
    session["user_name"]  = user.get("name", "User")
    session["user_email"] = user.get("email", "")
    session["role"]       = user.get("role", "staff")
    session["_st"]        = secrets.token_hex(16)   # session token — cleared on logout
    session["_lt"]        = datetime.datetime.utcnow().isoformat()
    return redirect(url_for("dashboard.index"))

@auth_bp.route("/register", methods=["GET"])
def register_page():
    if session.get("user_id"):
        return redirect(url_for("dashboard.index"))
    return render_template("register.html")

@auth_bp.route("/register", methods=["POST"])
def register():
    name     = request.form.get("name", "").strip()
    email    = request.form.get("email", "").strip()
    password = request.form.get("password", "")
    role     = request.form.get("role", "staff")
    if not all([name, email, password]):
        flash("All fields are required.", "error")
        return render_template("register.html")
    user, error = register_user(name, email, password, role)
    if error:
        flash(error, "error")
        return render_template("register.html")
    flash("Registration successful! Please log in.", "success")
    return redirect(url_for("auth.login_page"))

@auth_bp.route("/logout")
def logout():
    session.clear()
    resp = redirect(url_for("auth.login_page"))
    resp.delete_cookie("session")   # kill the cookie immediately
    resp.headers["Cache-Control"] = "no-store, no-cache, must-revalidate"
    flash("Logged out successfully.", "success")
    return resp
