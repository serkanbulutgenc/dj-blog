from .base import *  # noqa

DATABASES["default"]["NAME"] = BASE_DIR.parent / "db.sqlite3"

DATABASES["default"]["ATOMIC_REQUESTS"] = True

CORS_ALLOWED_ORIGINS = [
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]
