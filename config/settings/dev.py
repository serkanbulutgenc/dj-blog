from .base import *  # noqa

DATABASES["default"]["NAME"] = BASE_DIR.parent / "db.sqlite3"

DATABASES["default"]["ATOMIC_REQUESTS"] = True

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

HEADLESS_FRONTEND_URLS = {
    "account_confirm_email": "https://app.project.org/account/verify-email/{key}",
    # Key placeholders are automatically populated. You are free to adjust this
    # to your own needs, e.g.
    #
    # "https://app.project.org/account/email/verify-email?token={key}",
    "account_reset_password": "https://app.project.org/account/password/reset",
    "account_reset_password_from_key": "https://app.project.org/account/password/reset/key/{key}",
    "account_signup": "https://app.project.org/account/signup",
    # Fallback in case the state containing the `next` URL is lost and the handshake
    # with the third-party provider fails.
    "socialaccount_login_error": "https://app.project.org/account/provider/callback",
}

CORS_ALLOW_ALL_ORIGINS=True
CORS_ALLOWED_ORIGINS = [
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "https://refinemui-fbik--5173--b894c784.local-credentialless.webcontainer.io"
]
