# =============================================================
# settings.py
# Django's master configuration file.
# =============================================================

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# ── Security ──────────────────────────────────────────────────
# CHANGE THIS before deploying to production!
SECRET_KEY = "django-insecure-iipms-change-this-key-before-deployment-2026"

DEBUG = True

ALLOWED_HOSTS = ["*"]   # tighten to your domain in production


# ── Installed Apps ────────────────────────────────────────────
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "iipms_app",
]


# ── Middleware ────────────────────────────────────────────────
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",   # serves static files in production
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "iipms_project.urls"


# ── Templates ─────────────────────────────────────────────────
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "iipms_project.wsgi.application"


# ── Database ─────────────────────────────────────────────────
# SQLite for development — switch to PostgreSQL for production
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME":   BASE_DIR / "db.sqlite3",
    }
}

# PostgreSQL (uncomment for production):
# DATABASES = {
#     "default": {
#         "ENGINE":   "django.db.backends.postgresql",
#         "NAME":     os.environ.get("PGDATABASE", "iipms_db"),
#         "USER":     os.environ.get("PGUSER",     "iipms_user"),
#         "PASSWORD": os.environ.get("PGPASSWORD", ""),
#         "HOST":     os.environ.get("PGHOST",     "localhost"),
#         "PORT":     os.environ.get("PGPORT",     "5432"),
#     }
# }


# ── Custom User Model ─────────────────────────────────────────
AUTH_USER_MODEL = "iipms_app.User"


# ── Password Validation ───────────────────────────────────────
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
     "OPTIONS": {"min_length": 6}},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
]


# ── Login / Logout ────────────────────────────────────────────
LOGIN_URL          = "/login/"
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/"


# ── Internationalisation ──────────────────────────────────────
LANGUAGE_CODE = "en-au"
TIME_ZONE     = "Australia/Sydney"
USE_I18N      = True
USE_TZ        = True


# ── Static Files ─────────────────────────────────────────────
STATIC_URL       = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT      = BASE_DIR / "staticfiles"

# WhiteNoise: serves static files properly in production (Railway, etc.)
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"


# ── Media Files (uploads: photos, CVs) ───────────────────────
MEDIA_URL  = "/media/"
MEDIA_ROOT = BASE_DIR / "media"


# ── Email ─────────────────────────────────────────────────────
# Development: print emails to terminal
EMAIL_BACKEND  = "django.core.mail.backends.console.EmailBackend"
DEFAULT_FROM_EMAIL = "noreply@iipms.edu.au"


# ── Flash Message CSS Classes ─────────────────────────────────
from django.contrib.messages import constants as messages_constants
MESSAGE_TAGS = {
    messages_constants.SUCCESS: "success",
    messages_constants.ERROR:   "danger",
    messages_constants.WARNING: "warning",
    messages_constants.INFO:    "info",
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
