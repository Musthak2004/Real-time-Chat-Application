import os

from .settings import *  # noqa: F403

# ─── Security ────────────────────────────────────────────
SECRET_KEY = os.environ["SECRET_KEY"]

DEBUG = False

ALLOWED_HOSTS = [
    os.environ.get("PYTHONANYWHERE_DOMAIN", "yourusername.pythonanywhere.com"),
]

# PythonAnywhere handles HTTPS at the proxy level, so no redirect needed
SECURE_SSL_REDIRECT = False
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"

# ─── Database ────────────────────────────────────────────
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.path.join(os.environ.get("HOME", ""), "db.sqlite3"),
    }
}

# ─── Channels (in-memory — no Redis on free plan) ───────
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer",
    },
}

# ─── Celery (run synchronously — no worker on free plan) ─
CELERY_TASK_ALWAYS_EAGER = True
CELERY_BROKER_URL = ""

# ─── Static & Media files ───────────────────────────────
STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(os.environ.get("HOME", ""), "staticfiles")
STATICFILES_DIRS = [str(BASE_DIR / "static")]

MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(os.environ.get("HOME", ""), "media")

# ─── Email ───────────────────────────────────────────────
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = os.environ.get("EMAIL_HOST", "smtp.gmail.com")
EMAIL_PORT = int(os.environ.get("EMAIL_PORT", 587))
EMAIL_USE_TLS = os.environ.get("EMAIL_USE_TLS", "True") == "True"
EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD", "")
DEFAULT_FROM_EMAIL = os.environ.get("DEFAULT_FROM_EMAIL", "noreply@example.com")

# ─── Admin & error reporting ─────────────────────────────
ADMINS = [("Admin", os.environ.get("ADMIN_EMAIL", "admin@example.com"))]
MANAGERS = ADMINS

# ─── Logging ─────────────────────────────────────────────
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {process:d} {thread:d} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "level": "WARNING",
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
        "mail_admins": {
            "level": "ERROR",
            "class": "django.utils.log.AdminEmailHandler",
        },
    },
    "loggers": {
        "django": {
            "handlers": ["console", "mail_admins"],
            "level": "WARNING",
            "propagate": True,
        },
        "django.request": {
            "handlers": ["mail_admins", "console"],
            "level": "ERROR",
            "propagate": False,
        },
    },
}

# ─── Performance ─────────────────────────────────────────
CONN_MAX_AGE = int(os.environ.get("CONN_MAX_AGE", 60))
SESSION_ENGINE = "django.contrib.sessions.backends.signed_cookies"

# ─── Silence false-positive warnings ─────────────────────
# PythonAnywhere terminates HTTPS at the proxy, so Django SSL redirect is not needed
SILENCED_SYSTEM_CHECKS = ["security.W008"]
