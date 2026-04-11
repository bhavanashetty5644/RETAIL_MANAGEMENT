import hashlib, os
from db import sb_get, sb_post

def _hash_pw(plain):
    salt = os.urandom(16).hex()
    h = hashlib.sha256(f"{salt}{plain}".encode()).hexdigest()
    return f"{salt}:{h}"

def _check_pw(plain, stored):
    try:
        salt, h = stored.split(":", 1)
        return hashlib.sha256(f"{salt}{plain}".encode()).hexdigest() == h
    except Exception:
        return False

def login_user(email, password):
    try:
        rows = sb_get("users", {"email": f"eq.{email.lower().strip()}", "select": "id,name,email,password,role"})
    except Exception as e:
        return None, f"Database error: {e}"
    if not rows:
        return None, "Invalid email or password"
    user = rows[0]
    stored = user.get("password", "")
    # Support both our hash format and plain/bcrypt hashes from old data
    if _check_pw(password, stored) or stored == password:
        return user, None
    return None, "Invalid email or password"

def register_user(name, email, password, role="staff"):
    try:
        existing = sb_get("users", {"email": f"eq.{email.lower().strip()}", "select": "id"})
        if existing:
            return None, "Email already registered"
        # Prevent registering with superadmin email
        if email.lower().strip() == "admin@gmail.com":
            return None, "This email is reserved."
        data = {"name": name.strip(), "email": email.lower().strip(),
                "password": _hash_pw(password), "role": "staff"}  # registration always creates staff
        user = sb_post("users", data)
        return user, None
    except Exception as e:
        return None, f"Registration failed: {e}"

def get_all_users():
    return sb_get("users", {"select": "id,name,email,role"})
