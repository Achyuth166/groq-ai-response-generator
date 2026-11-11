import os
from pathlib import Path

from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables from backend/.env
BASE_DIR = Path(__file__).resolve().parents[2]
load_dotenv(BASE_DIR / ".env")

# Get Supabase credentials
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Check credentials
if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("Supabase credentials are missing in .env")

# Create Supabase connection
supabase: Client = create_client(
    SUPABASE_URL,
    SUPABASE_KEY
)

print("Supabase connection initialized successfully!")