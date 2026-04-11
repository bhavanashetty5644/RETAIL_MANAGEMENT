import os
from datetime import timedelta
from dotenv import load_dotenv
load_dotenv()

class Config:
    SECRET_KEY               = os.environ.get("SECRET_KEY", "RetailOS_SuperSecret_2305_Flask_Prod")
    SUPABASE_URL             = os.environ.get("SUPABASE_URL", "")
    SUPABASE_KEY             = os.environ.get("SUPABASE_KEY", "")
    SESSION_COOKIE_HTTPONLY  = True
    SESSION_COOKIE_SAMESITE  = "Lax"
    SESSION_COOKIE_SECURE    = False   # set True for HTTPS
    PERMANENT_SESSION_LIFETIME = timedelta(hours=8)
