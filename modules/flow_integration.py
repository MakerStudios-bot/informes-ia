"""
Integración con Flow.com para crear links de pago automáticamente
"""
import os
import requests
import hmac
import hashlib
from dotenv import load_dotenv

load_dotenv()

FLOW_API_KEY = os.getenv("FLOW_API_KEY", "4C58F2DC-0ADE-44C0-8A4B-46F7L335B4F9")
FLOW_SECRET_KEY = os.getenv("FLOW_SECRET_KEY", "decc9f98111122170ad2a969ec9cc597f71d6045")
FLOW_API_URL = "https://api.flow.cl/api"

PRECIOS = {
    "due_diligence": 29990,
    "mercado": 19990,
    "persona": 9990,
    "competencia": 24990,
}

def crear_link_pago(tipo: str, objetivo: str, email: str, nombre: str) -> str:
    """
    Crea un link de pago en Flow.

    Args:
        tipo: Tipo de informe (due_diligence, mercado, persona, competencia)
        objetivo: Empresa o persona a investigar
        email: Email del cliente
        nombre: Nombre del cliente

    Returns:
        URL del link de pago
    """
    amount = PRECIOS.get(tipo, 29990)

    # Datos para crear el link
    data = {
        "apiKey": FLOW_API_KEY,
        "commerceOrder": f"{tipo}_{int(__import__('time').time())}",
        "subject": f"Informe {tipo} - {objetivo}",
        "currency": "CLP",
        "amount": amount,
        "email": email,
        "payer": nombre,
        "successUrl": "https://informes-ia.com/success",
        "failureUrl": "https://informes-ia.com/failure",
        "requestToken": _generar_token(
            f"{FLOW_API_KEY}{tipo}_{int(__import__('time').time())}{amount}CLP{email}"
        ),
    }

    try:
        response = requests.post(
            f"{FLOW_API_URL}/paymentlinks/",
            data=data,
            timeout=10
        )
        response.raise_for_status()
        result = response.json()

        if result.get("url"):
            return result["url"]
        else:
            raise Exception(f"Error creando link: {result.get('message', 'Unknown error')}")

    except Exception as e:
        print(f"Error en Flow API: {e}")
        raise

def validar_webhook(x_hub_signature: str, payload: bytes) -> bool:
    """
    Valida la firma HMAC del webhook de Flow.

    Args:
        x_hub_signature: Header X-Hub-Signature de Flow
        payload: Body del webhook (bytes)

    Returns:
        True si es válido, False si no
    """
    expected_signature = f"sha256={hmac.new(
        FLOW_SECRET_KEY.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()}"

    return hmac.compare_digest(x_hub_signature, expected_signature)

def _generar_token(data: str) -> str:
    """Genera token para Flow API"""
    return hashlib.md5(data.encode()).hexdigest()
