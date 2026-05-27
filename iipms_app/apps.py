# =============================================================
# apps.py
# Tells Django about our app's configuration.
# =============================================================

from django.apps import AppConfig


class IipmsAppConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name               = "iipms_app"
    verbose_name       = "IIPMS — Intelligent Internship Placement"
