"""
wsgi.py
WSGI config for the IIPMS project.

This is the entry point for WSGI-compatible web servers
(Apache with mod_wsgi, Gunicorn, etc.) to serve the Django app.

For local development, use:
    python manage.py runserver

For production with Gunicorn:
    gunicorn iipms_project.wsgi:application
"""

import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "iipms_project.settings")
application = get_wsgi_application()
