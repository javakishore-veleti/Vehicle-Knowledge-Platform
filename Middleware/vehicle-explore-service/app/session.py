"""Decrypt the X-VKP-Session token minted by the Java vkp-session-security library.

Wire-compatible with SessionCryptoService: token = base64url( iv[12] || AES-256-GCM(ct+tag) ),
key = base64 of a 32-byte secret (VKP_SESSION_SECRET, identical across services).
"""
import base64
import json
import logging
from typing import Optional

from . import config

log = logging.getLogger("vehicle-explore.session")


def decrypt_session(token: Optional[str]) -> Optional[dict]:
    if not token or not config.SESSION_SECRET:
        return None
    try:
        from cryptography.hazmat.primitives.ciphers.aead import AESGCM
        key = base64.b64decode(config.SESSION_SECRET)
        raw = base64.urlsafe_b64decode(token + "=" * (-len(token) % 4))
        iv, ct = raw[:12], raw[12:]
        plain = AESGCM(key).decrypt(iv, ct, None)
        return json.loads(plain.decode("utf-8"))   # {sessionId, userType, userId, issuedAt}
    except Exception as e:  # noqa: BLE001 — bad/foreign token -> anonymous
        log.debug("session token not decryptable: %s", e)
        return None
