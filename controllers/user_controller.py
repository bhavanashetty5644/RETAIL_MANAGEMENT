import hashlib, os
from db import sb_get, sb_post, sb_patch, sb_delete
from flask import session


def _hash_pw(plain):
    salt = os.urandom(16).hex()
    h = hashlib.sha256(f"{salt}{plain}".encode()).hexdigest()
    return f"{salt}:{h}"


def get_all_users():
    return sb_get("users", {"select": "id,name,email,role", "order": "id.asc"})


def get_user(uid):
    rows = sb_get("users", {"id": f"eq.{uid}", "select": "id,name,email,role"})
    return rows[0] if rows else None


def create_user(name, email, password, role="staff"):
    email = email.lower().strip()
    # Admins can only create staff; superadmin can create any role
    current_role = session.get("role", "staff")
    if current_role == "admin" and role not in ("staff",):
        return None, "Admins can only create staff users"
    existing = sb_get("users", {"email": f"eq.{email}", "select": "id"})
    if existing:
        return None, "Email already registered"
    if len(password) < 6:
        return None, "Password must be at least 6 characters"
    data = {
        "name": name.strip(),
        "email": email,
        "password": _hash_pw(password),
        "role": role,
    }
    user = sb_post("users", data)
    if not user or not user.get("id"):
        return None, "Failed to create user. Check Supabase service key and RLS policies."
    return user, None


def update_user(uid, name, email, role, password=None):
    current_role = session.get("role", "staff")
    current_uid = session.get("user_id")

    # Prevent admins from editing admins or superadmins (except themselves for name/email)
    target = get_user(uid)
    if target:
        if current_role == "admin":
            if target["role"] in ("admin", "superadmin") and target["id"] != current_uid:
                raise PermissionError("Admins cannot edit other admins or superadmins")
            # Admins can only promote to staff level
            if role in ("admin", "superadmin"):
                role = target["role"]  # keep existing role, don't allow promotion

    # Nobody can change superadmin's role except superadmin
    if target and target["role"] == "superadmin" and current_role != "superadmin":
        role = "superadmin"

    data = {"name": name.strip(), "email": email.lower().strip(), "role": role}
    if password:
        if len(password) < 6:
            raise ValueError("Password must be at least 6 characters")
        data["password"] = _hash_pw(password)
    return sb_patch("users", uid, data)


def delete_user(uid):
    target = get_user(uid)
    if target and target["role"] == "superadmin":
        raise PermissionError("Superadmin account cannot be deleted")
    return sb_delete("users", uid)


def promote_to_admin(uid):
    """Promote a staff user to admin. Only superadmin can do this."""
    target = get_user(uid)
    if not target:
        raise ValueError("User not found")
    if target["role"] == "superadmin":
        raise PermissionError("Cannot change superadmin role")
    return sb_patch("users", uid, {"role": "admin"})


def demote_to_staff(uid):
    """Demote an admin to staff. Only superadmin can do this."""
    target = get_user(uid)
    if not target:
        raise ValueError("User not found")
    if target["role"] == "superadmin":
        raise PermissionError("Cannot change superadmin role")
    return sb_patch("users", uid, {"role": "staff"})
