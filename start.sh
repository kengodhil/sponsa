#!/usr/bin/env bash
# Runtime entrypoint. Internal Postgres is reachable here.
set -o errexit
python backend/manage.py migrate --noinput
python backend/manage.py collectstatic --noinput
exec gunicorn --chdir backend config.wsgi:application
