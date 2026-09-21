import os

import django
from django.core.management import call_command
from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

skip = {"1", "true", "yes", "on"}
if os.environ.get("SKIP_MIGRATE_ON_BOOT", "").strip().lower() not in skip:
    call_command("migrate", interactive=False, verbosity=1)
if os.environ.get("SKIP_COLLECTSTATIC_ON_BOOT", "").strip().lower() not in skip:
    call_command("collectstatic", interactive=False, verbosity=1)
if os.environ.get("SKIP_SEED_DEMO", "").strip().lower() not in skip:
    call_command("seed_demo", verbosity=1)

application = get_wsgi_application()
