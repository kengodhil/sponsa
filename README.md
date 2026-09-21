Sponsa
======

Ladies enter with a Tanzania mobile number, view sponsor photos, pay 15,000 TZS, then open the full profile and chat. Sponsor men post a photo and pay a listing fee.

Run locally
-----------
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
cd backend
python manage.py migrate
python manage.py seed_demo
python manage.py runserver

Demo accounts after seed_demo
-----------------------------
Admin   255700000001 / AdminPass123
Lady    enter with 255712000002 (or any new 07 number)
Man     255713000003 / ManPass123

Selcom (demo now, live later)
-----------------------------
Keep SELCOM_SANDBOX=True until you have live keys.
Then set SELCOM_API_KEY, SELCOM_API_SECRET, SELCOM_VENDOR and SELCOM_SANDBOX=False.
Webhook: /pay/selcom/webhook/
PUBLIC_BASE_URL must be your live https URL.

Deploy on Render (recommended)
------------------------------
1. Push this repo and create a Blueprint from render.yaml.
2. Set DJANGO_ALLOWED_HOSTS to your onrender.com host.
3. Set CSRF_TRUSTED_ORIGINS and PUBLIC_BASE_URL to https://YOUR-APP.onrender.com
4. Set **Start Command** (Settings — required if the service was created by hand, not from the Blueprint):

   python backend/manage.py migrate --noinput && gunicorn --chdir backend config.wsgi:application

   Do **not** run migrate in the Build Command. Render's internal Postgres host is not reachable while the image is building, which is what caused `relation "sponsors_sponsorprofile" does not exist`.
5. Set DJANGO_DEBUG=False.
6. Run `python backend/manage.py seed_demo` once from the Render shell if you want sample men.
7. When going live, paste Selcom keys and set SELCOM_SANDBOX=False.

Vercel
------
This is a Django app with payments and a database. Host it on Render (or another always-on server). Vercel is a fit later if you add a separate frontend; vercel.json is only a starter and will not replace Render for Selcom webhooks and Postgres.
