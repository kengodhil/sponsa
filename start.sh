#!/usr/bin/env bash
# Runtime entrypoint. Internal Postgres is reachable here.
set -o errexit
python backend/manage.py migrate --noinput
python backend/manage.py collectstatic --noinput
python backend/manage.py seed_demo
exec gunicorn --chdir backend config.wsgi:application
