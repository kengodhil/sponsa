"""Snippe payment gateway client — https://docs.snippe.sh"""
import uuid

import requests
from django.conf import settings


class SnippeError(Exception):
    pass


class SnippeClient:
    def __init__(self):
        self.api_key = getattr(settings, "SNIPPE_API_KEY", "") or ""
        self.base_url = getattr(settings, "SNIPPE_BASE_URL", "https://api.snippe.sh").rstrip("/")
        self.sandbox = getattr(settings, "SNIPPE_SANDBOX", True)

    def _headers(self, idempotency_key=None):
        h = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        if idempotency_key:
            h["Idempotency-Key"] = idempotency_key
        return h

    def create_mobile_payment(self, amount, phone, firstname, lastname, webhook_url, metadata=None):
        """Create USSD-push mobile money payment. Amount in TZS integer."""
        if self.sandbox and not self.api_key:
            ref = f"demo-{uuid.uuid4().hex[:12]}"
            return {
                "status": "success",
                "code": 201,
                "data": {
                    "reference": ref,
                    "status": "pending",
                    "amount": {"currency": "TZS", "value": amount},
                    "payment_type": "mobile",
                    "demo": True,
                },
            }

        payload = {
            "payment_type": "mobile",
            "details": {"amount": int(amount), "currency": "TZS"},
            "phone_number": phone if phone.startswith("255") else f"255{phone.lstrip('0')}",
            "customer": {
                "firstname": firstname or "User",
                "lastname": lastname or "Customer",
                "email": f"{phone}@sponsorsconnection.tz",
            },
            "webhook_url": webhook_url,
            "metadata": metadata or {},
        }
        try:
            r = requests.post(
                f"{self.base_url}/v1/payments",
                json=payload,
                headers=self._headers(idempotency_key=str(uuid.uuid4())),
                timeout=30,
            )
            data = r.json() if r.content else {}
            if r.status_code not in (200, 201) or data.get("status") == "error":
                raise SnippeError(data.get("message") or f"Snippe error {r.status_code}")
            return data
        except requests.RequestException as exc:
            raise SnippeError(str(exc)) from exc

    def get_payment(self, reference):
        if self.sandbox and not self.api_key:
            return {"status": "success", "data": {"reference": reference, "status": "pending"}}
        try:
            r = requests.get(
                f"{self.base_url}/v1/payments/{reference}",
                headers=self._headers(),
                timeout=20,
            )
            data = r.json() if r.content else {}
            if r.status_code != 200:
                raise SnippeError(data.get("message") or f"Status {r.status_code}")
            return data
        except requests.RequestException as exc:
            raise SnippeError(str(exc)) from exc
