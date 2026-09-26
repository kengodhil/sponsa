Sponsors Connection
===================

Users join with a Tanzania mobile number, browse rich men and women sponsors (admin-added only), pay **10,000 TZS** to unlock a profile, then **5,000 TZS** to chat.

Payments via **Snippe** (mobile money USSD push).

Run locally
-----------
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
cd backend
python manage.py migrate
python manage.py seed_demo
python manage.py runserver
```

Demo after seed_demo
--------------------
- Admin: `255700000001` / `AdminPass123`
- User: enter any `07…` number on join

Env
---
- `UNLOCK_FEE_TZS=10000`
- `CHAT_FEE_TZS=5000`
- `SNIPPE_API_KEY=` (empty = demo sandbox)
- `SNIPPE_SANDBOX=True`
- Webhook: `/pay/snippe/webhook/`

Admin only adds sponsors. Cards show men and women.
