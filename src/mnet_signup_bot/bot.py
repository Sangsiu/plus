
from __future__ import annotations
import json
import logging
import random
import string
from dataclasses import dataclass
from typing import List, Optional, Dict, Any

import requests

from .http import make_session

AUTH_TOKEN_URL = "https://www.mnetplus.world/api/account-service/v1/user/email/authToken"
SAVE_TMP_URL = "https://www.mnetplus.world/api/account-service/v1/user/signup/save-tmp"

def rand_device_name(prefix: str = "python-bot", length: int = 6) -> str:
    import secrets
    alphabet = string.ascii_lowercase + string.digits
    suffix = ''.join(secrets.choice(alphabet) for _ in range(length))
    return f"{prefix}-{suffix}"

@dataclass
class SignupInput:
    email: str
    password: str
    gender: str = "m"           # "m"/"f"
    birth_year: str = "1998"    # YYYY string
    locale: str = "en"
    device_name: Optional[str] = None
    optional_terms: Optional[List[Dict[str, Any]]] = None

    def to_auth_payload(self) -> Dict[str, Any]:
        return {
            "email": self.email,
            "purpose": "signup",
            "locale": self.locale,
            "deviceName": self.device_name or rand_device_name(),
        }

    def to_save_tmp_payload(self, auth_token: str) -> Dict[str, Any]:
        payload = {
            "email": self.email,
            "password": self.password,
            "gender": self.gender,
            "birthDate": str(self.birth_year),
            "authToken": auth_token,
        }
        if self.optional_terms:
            payload["optionalTerms"] = self.optional_terms
        return payload

def _ensure_json_ok(resp: requests.Response, label: str) -> None:
    if resp.status_code >= 400:
        raise RuntimeError(f"{label} HTTP {resp.status_code}: {resp.text[:300]}")
    try:
        resp.json()
    except Exception as e:
        raise RuntimeError(f"{label} returned non-JSON: {e}; body={resp.text[:300]}")

def get_auth_token(session: requests.Session, req: SignupInput) -> str:
    resp = session.post(AUTH_TOKEN_URL, json=req.to_auth_payload())
    _ensure_json_ok(resp, "authToken")
    data = resp.json()
    if not (isinstance(data, dict) and data.get("success") is True):
        raise RuntimeError(f"authToken failed: {data}")
    token = data.get("data", {}).get("token")
    if not token:
        raise RuntimeError(f"authToken missing token: {data}")
    logging.debug("Auth token resp: %s", json.dumps(data, ensure_ascii=False))
    return token

def save_tmp_signup(session: requests.Session, req: SignupInput, auth_token: str) -> None:
    payload = req.to_save_tmp_payload(auth_token)
    resp = session.post(SAVE_TMP_URL, json=payload)
    _ensure_json_ok(resp, "save-tmp")
    data = resp.json()
    if not (isinstance(data, dict) and data.get("success") is True):
        raise RuntimeError(f"save-tmp failed: {data}")
    logging.debug("Save tmp resp: %s", json.dumps(data, ensure_ascii=False))

def run_single(email: str, password: str, gender: str = "m", birth_year: str = "1998",
               locale: str = "en", device_name: str | None = None,
               marketing_terms_version: str | None = None,
               timeout: int = 30, retries: int = 3, backoff: float = 0.5) -> None:
    session = make_session(timeout=timeout, retries=retries, backoff=backoff)
    optional_terms = None
    if marketing_terms_version:
        optional_terms = [{"termsId": "marketing", "termsVer": str(marketing_terms_version)}]
    req = SignupInput(
        email=email,
        password=password,
        gender=gender,
        birth_year=str(birth_year),
        locale=locale,
        device_name=device_name,
        optional_terms=optional_terms,
    )
    logging.info("Requesting auth token for %s ...", email)
    token = get_auth_token(session, req)
    logging.info("Auth token acquired. Submitting save-tmp ...")
    save_tmp_signup(session, req, token)
    logging.info("Done: signup save-tmp OK for %s", email)

