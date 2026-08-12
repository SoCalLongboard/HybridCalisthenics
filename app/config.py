import os


DATABASE_PATH = os.environ.get("DATABASE_PATH", "./data/hybrid-tracker.db")
PORT = int(os.environ.get("PORT", "8000"))
SECRET_KEY = os.environ.get("SECRET_KEY", "dev-insecure-secret-key-change-me")
SECURE_COOKIES = os.environ.get("SECURE_COOKIES", "true").lower() == "true"
SESSION_MAX_AGE = int(os.environ.get("SESSION_MAX_AGE", str(60 * 60 * 24 * 30)))  # 30 days
