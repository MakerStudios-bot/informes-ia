"""
Integración con Flow.com para crear links de pago automáticamente
"""
import os
import requests
import hmac
import hashlib
import time
from dotenv import load_dotenv

load_dotenv()

FLOW_API_KEY = os.getenv("FLOW_API_KEY", "4C58F2DC-0ADE-44C0-8A4B-46F7L335B4F9")
FLOW_SECRET_KEY = os.getenv("FLOW_SECRET_KEY", "decc9f98111122170ad2a969ec9cc597f71d6045")
FLOW_API_URL = "https://www.flow.cl/api"

PRECIOS = {
    "due_diligence": 29990,
    "mercado": 19990,
    "persona": 9990,
    "competencia": 24990,
}

def crear_link_pago(tipo: str, objetivo: str, email: str, nombre: str) -> str:
    """
    Crea un link de pago en Flow usando la API.

    Args:
        tipo: Tipo de informe (due_diligence, mercado, persona, competencia)
        objetivo: Empresa o persona a investigar
        email: Email del cliente
        nombre: Nombre del cliente

    Returns:
        URL del link de pago
    """
    amount = PRECIOS.get(tipo, 29990)
    commerce_order = f"{tipo}_{int(time.time())}"

    # Preparar parámetros para Flow
    params = {
        "apiKey": FLOW_API_KEY,
        "amount": str(amount),
        "currency": "CLP",
        "commerceOrder": commerce_order,
        "subject": f"Informe {tipo} - {objetivo}",
        "email": email,
        "payerEmail": email,
        "returnUrl": "https://informes-ia.com/success",
    }

    # Firmar la solicitud según requiere Flow
    signature = _firmar_parametros(params)
    params["s"] = signature

    try:
        response = requests.post(
            f"{FLOW_API_URL}/payment/create",
            data=params,
            timeout=10
        )
        response.raise_for_status()

        # Flow devuelve HTML o JSON con redirect
        if "url" in response.text:
            # Buscar la URL en la respuesta
            import re
            match = re.search(r'https?://[^\s"<>]+', response.text)
            if match:
                return match.group(0)

        # Si es JSON
        result = response.json() if response.headers.get('content-type') == 'application/json' else {}
        if result.get("url"):
            return result["url"]

        # Si es respuesta HTML con redirect
        if response.status_code == 200:
            return response.url

        raise Exception(f"Error creando link: {response.text}")

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
    expected_signature = hmac.new(
        FLOW_SECRET_KEY.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()

    return hmac.compare_digest(x_hub_signature, expected_signature)

def _firmar_parametros(params: dict) -> str:
    """
    Firma los parámetros según el método de Flow.

    Ordena alfabéticamente y concatena como parameterNamevalue,
    luego firma con HMAC-SHA256.
    """
    # Ordenar alfabéticamente
    sorted_params = sorted(params.items())

    # Concatenar como parameterNamevalue
    to_sign = "".join([f"{k}{v}" for k, v in sorted_params])

    # Firmar con HMAC-SHA256
    signature = hmac.new(
        FLOW_SECRET_KEY.encode(),
        to_sign.encode(),
        hashlib.sha256
    ).hexdigest()

    return signature
