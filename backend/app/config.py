
import os
from pathlib import Path
from dotenv import load_dotenv

# Find the backend folder
BACKEND_DIR = Path(__file__).resolve().parent.parent

# Find the .env file inside backend
ENV_FILE = BACKEND_DIR / ".env"

# Load environment variables from .env
load_dotenv(ENV_FILE, override=True)

# Read Groq configuration
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "").strip()
GROQ_MODEL = os.getenv(
    "GROQ_MODEL",
    "openai/gpt-oss-120b",
).strip()
