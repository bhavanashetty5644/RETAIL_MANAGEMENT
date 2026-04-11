"""
Utility: generate a hashed password for manual DB insertion.
Usage:  python hash_password.py
"""
import hashlib, os, getpass

password = getpass.getpass("Enter password to hash: ")
salt = os.urandom(16).hex()
h    = hashlib.sha256(f"{salt}{password}".encode()).hexdigest()
print(f"\nHashed password:\n{salt}:{h}\n")
print("Paste this into your users table 'password' column.")
