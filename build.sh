#!/usr/bin/env bash
# Build only. Do NOT migrate here: Render's internal DATABASE_URL
# (dpg-...-a) is not reachable during the build phase, so migrate
# would either fail the deploy or silently apply to a throwaway SQLite file.
set -o errexit
pip install -r requirements.txt
python backend/manage.py collectstatic --noinput
