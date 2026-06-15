import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
AUTH_SECRET = os.getenv("AUTH_SECRET")

if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY is not set. Please add it to your .env file.")

if not AUTH_SECRET:
    raise ValueError("AUTH_SECRET is not set. Please add it to your .env file.")
