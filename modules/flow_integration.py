"""
Integración con Flow.com - Validación de webhooks
"""
import os
import hmac
import hashlib
from dotenv import load_dotenv

load_dotenv()

FLOW_SECRET_KEY = os.getenv("FLOW_SECRET_KEY", "decc9f98111122170ad2a969ec9cc597f71d6045")

PRECIOS = {
    "due_diligence": 29990,
    "mercado": 19990,
    "persona": 9990,
    "competencia": 24990,
}

def validar_webhook(request_body: bytes, signature_header: str) -> bool:
    """
    Valida la firma HMAC del webhook de Flow.

    Args:
        request_body: Body del webhook (bytes)
        signature_header: Header X-Hub-Signature de Flow

    Returns:
        True si es válido, False si no
    """
    expected_signature = hmac.new(
        FLOW_SECRET_KEY.encode(),
        request_body,
        hashlib.sha256
    ).hexdigest()

    return hmac.compare_digest(signature_header, expected_signature)
