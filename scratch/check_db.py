import os
import requests
from dotenv import load_dotenv

load_dotenv()

URL = os.environ.get("SUPABASE_URL")
KEY = os.environ.get("SUPABASE_SERVICE_KEY") or os.environ.get("SUPABASE_KEY")

headers = {
    "apikey": KEY,
    "Authorization": f"Bearer {KEY}",
    "Content-Type": "application/json"
}

def check(table):
    print(f"Checking table: {table}")
    r = requests.get(f"{URL}/rest/v1/{table}?select=count", headers=headers)
    if r.ok:
        print(f"  Count: {r.json()}")
    else:
        print(f"  Error {r.status_code}: {r.text}")

tables = ["users", "products", "suppliers", "procurement", "sales"]
for t in tables:
    check(t)
