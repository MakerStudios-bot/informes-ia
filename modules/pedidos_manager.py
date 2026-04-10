"""
Gestor de pedidos - almacenamiento persistente
"""
import json
from pathlib import Path
from datetime import datetime
from typing import Optional

PEDIDOS_FILE = Path(__file__).parent.parent / "pedidos.json"

def crear_pedido(tipo: str, objetivo: str, email: str, nombre: str, datos_extra: str = "") -> dict:
    """Crea un nuevo pedido y lo guarda"""
    pedido = {
        "id": int(datetime.now().timestamp() * 1000),
        "tipo": tipo,
        "objetivo": objetivo,
        "email": email,
        "nombre": nombre,
        "datos_extra": datos_extra,
        "estado": "pendiente",
        "fecha_creacion": datetime.now().isoformat(),
        "fecha_pago": None,
        "link_flow": None
    }

    pedidos = leer_pedidos()
    pedidos["pedidos"].append(pedido)
    guardar_pedidos(pedidos)

    return pedido

def obtener_pedido(email: str) -> Optional[dict]:
    """Obtiene el pedido más reciente de un cliente"""
    pedidos = leer_pedidos()
    # Buscar por email (el más reciente)
    coincidentes = [p for p in pedidos["pedidos"] if p["email"] == email]
    if coincidentes:
        return coincidentes[-1]  # El último
    return None

def actualizar_pedido(email: str, estado: str, link_flow: str = None) -> bool:
    """Actualiza el estado de un pedido"""
    pedidos = leer_pedidos()

    # Buscar y actualizar el pedido más reciente del cliente
    for p in reversed(pedidos["pedidos"]):
        if p["email"] == email:
            p["estado"] = estado
            if estado == "pagado":
                p["fecha_pago"] = datetime.now().isoformat()
            if link_flow:
                p["link_flow"] = link_flow
            guardar_pedidos(pedidos)
            return True

    return False

def leer_pedidos() -> dict:
    """Lee todos los pedidos"""
    if PEDIDOS_FILE.exists():
        with open(PEDIDOS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"pedidos": []}

def guardar_pedidos(pedidos: dict):
    """Guarda los pedidos"""
    with open(PEDIDOS_FILE, "w", encoding="utf-8") as f:
        json.dump(pedidos, f, indent=2, ensure_ascii=False)

def obtener_todos() -> list:
    """Obtiene todos los pedidos"""
    pedidos = leer_pedidos()
    return pedidos.get("pedidos", [])
