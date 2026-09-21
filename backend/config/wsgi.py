import os

from django.core.management import call_command
from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
application = get_wsgi_application()

# Render's internal Postgres is reachable at process boot, not during build.
# This creates sponsors_sponsorprofile (and the rest) even if the dashboard
# Start Command is still a bare gunicorn invocation.
if os.environ.get("SKIP_MIGRATE_ON_BOOT", "").strip().lower() not in {"1", "true", "yes", "on"}:
    call_command("migrate", interactive=False, verbosity=1)
