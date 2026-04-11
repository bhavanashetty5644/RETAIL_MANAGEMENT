from functools import wraps
from flask import session, redirect, url_for, request, jsonify

def _logged_in():
    return bool(session.get("user_id") and session.get("_st"))

def _is_superadmin():
    return session.get("role") == "superadmin"

def _is_admin_or_above():
    return session.get("role") in ("admin", "superadmin")

def login_required(f):
    @wraps(f)
    def dec(*a, **kw):
        if not _logged_in():
            session.clear()
            if request.is_json or "/api/" in request.path:
                return jsonify({"error": "Unauthorized"}), 401
            return redirect(url_for("auth.login_page"))
        return f(*a, **kw)
    return dec

def admin_required(f):
    @wraps(f)
    def dec(*a, **kw):
        if not _logged_in():
            session.clear()
            return redirect(url_for("auth.login_page"))
        if not _is_admin_or_above():
            if request.is_json or "/api/" in request.path:
                return jsonify({"error": "Admin only"}), 403
            return redirect(url_for("dashboard.index"))
        return f(*a, **kw)
    return dec

def superadmin_required(f):
    @wraps(f)
    def dec(*a, **kw):
        if not _logged_in():
            session.clear()
            return redirect(url_for("auth.login_page"))
        if not _is_superadmin():
            if request.is_json or "/api/" in request.path:
                return jsonify({"error": "Superadmin only"}), 403
            return redirect(url_for("dashboard.index"))
        return f(*a, **kw)
    return dec
