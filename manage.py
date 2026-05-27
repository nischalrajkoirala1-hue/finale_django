#!/usr/bin/env python
"""
manage.py
Django's command-line utility for administrative tasks.

Common commands:
    python manage.py runserver         -- start the development server
    python manage.py makemigrations    -- generate migration files from model changes
    python manage.py migrate           -- apply migrations to the database
    python manage.py createsuperuser   -- create an admin account
    python manage.py seed_data         -- populate demo data
    python manage.py collectstatic     -- gather static files for production
"""

import os
import sys


def main():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "iipms_project.settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed? "
            "Run:  pip install django"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
