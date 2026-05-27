#!/usr/bin/env bash
# Railway runs this script before starting the server.
# It installs packages, runs migrations, and collects static files.

set -o errexit   # exit on any error

pip install -r ../requirements.txt

python manage.py collectstatic --no-input
python manage.py migrate
