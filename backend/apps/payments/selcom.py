import base64
import hashlib
import hmac
from datetime import datetime
from urllib.parse import urlencode
from zoneinfo import ZoneInfo

import requests
from django.conf import settings


class SelcomError(Exception):
    pass


class SelcomClient:
    def __init__(self):
        self.base_url = settings.SELCOM_BASE_URL.rstrip("/")
        self.api_key = settings.SELCOM_API_KEY
        self.api_secret = settings.SELCOM_API_SECRET
        self.vendor = settings.SELCOM_VENDOR
        self.sandbox = settings.SELCOM_SANDBOX or not (self.api_key and self.api_secret and self.vendor)

    def _timestamp(self):
        return datetime.now(ZoneInfo("Africa/Dar_es_Salaam")).isoformat(timespec="seconds")

    def _headers(self, payload):
        timestamp = self._timestamp()
        signed_fields = ",".join(payload.keys())
        parts = [f"timestamp={timestamp}"] + [f"{key}={payload[key]}" for key in payload]
        signing_string = "&".join(parts)
        digest = base64.b64encode(
            hmac.new(
                self.api_secret.encode("utf-8"),
                signing_string.encode("utf-8"),
                hashlib.sha256,
            ).digest()
        ).decode("utf-8")
        auth = base64.b64encode(self.api_key.encode("utf-8")).decode("utf-8")
        return {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"SELCOM {auth}",
            "Digest-Method": "HS256",
            "Digest": digest,
            "Timestamp": timestamp,
            "Signed-Fields": signed_fields,
        }

    def post(self, path, payload):
        if self.sandbox:
            return {
                "reference": "SANDBOX",
                "resultcode": "111",
                "result": "PENDING",
                "message": "Demo mode. Confirm payment on the next screen.",
                "data": [],
                "sandbox": True,
            }
        url = f"{self.base_url}{path}"
        try:
            response = requests.post(url, json=payload, headers=self._headers(payload), timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as exc:
            raise SelcomError(str(exc)) from exc

    def get(self, path, params):
        if self.sandbox:
            return {
                "reference": "SANDBOX",
                "resultcode": "000",
                "result": "PENDING",
                "message": "Payment still waiting.",
                "data": [],
            }
        timestamp = self._timestamp()
        signed_fields = ",".join(params.keys())
        parts = [f"timestamp={timestamp}"] + [f"{key}={params[key]}" for key in params]
        signing_string = "&".join(parts)
        digest = base64.b64encode(
            hmac.new(
                self.api_secret.encode("utf-8"),
                signing_string.encode("utf-8"),
                hashlib.sha256,
            ).digest()
        ).decode("utf-8")
        auth = base64.b64encode(self.api_key.encode("utf-8")).decode("utf-8")
        headers = {
            "Accept": "application/json",
            "Authorization": f"SELCOM {auth}",
            "Digest-Method": "HS256",
            "Digest": digest,
            "Timestamp": timestamp,
            "Signed-Fields": signed_fields,
        }
        url = f"{self.base_url}{path}?{urlencode(params)}"
        try:
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as exc:
            raise SelcomError(str(exc)) from exc

    def create_order(self, order_id, buyer_name, buyer_phone, amount, webhook, remarks):
        payload = {
            "vendor": self.vendor or "SANDBOX",
            "order_id": order_id,
            "buyer_email": f"{buyer_phone}@sponsa.local",
            "buyer_name": buyer_name,
            "buyer_phone": buyer_phone,
            "amount": int(amount),
            "currency": "TZS",
            "webhook": base64.b64encode(webhook.encode("utf-8")).decode("utf-8"),
            "buyer_remarks": remarks,
            "merchant_remarks": remarks,
            "no_of_items": 1,
        }
        return self.post("/v1/checkout/create-order-minimal", payload)

    def wallet_push(self, transid, order_id, msisdn):
        payload = {
            "transid": transid,
            "order_id": order_id,
            "msisdn": msisdn,
        }
        return self.post("/v1/checkout/wallet-payment", payload)

    def order_status(self, order_id):
        return self.get("/v1/checkout/order-status", {"order_id": order_id})
