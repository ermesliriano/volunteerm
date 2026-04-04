from typing import Any, Dict

from google.oauth2 import id_token
from google.auth.transport import requests

GOOGLE_ISSUERS = {"accounts.google.com", "https://accounts.google.com"}

def verify_google_id_token(token: str, client_id: str) -> Dict[str, Any]:
    """
    Verifica un ID token (JWT) emitido por Google para Sign in with Google.

    - Valida firma y exp.
    - Valida audience (aud) contra client_id.
    - Valida issuer (iss) sea un issuer esperado.
    """
    if not client_id:
        raise ValueError("GOOGLE_CLIENT_ID no configurado en el backend.")
    if not token:
        raise ValueError("Token vacío.")

    req = requests.Request()
    idinfo = id_token.verify_oauth2_token(token, req, client_id)

    iss = idinfo.get("iss")
    if iss not in GOOGLE_ISSUERS:
        raise ValueError("Issuer inválido.")

    return idinfo
