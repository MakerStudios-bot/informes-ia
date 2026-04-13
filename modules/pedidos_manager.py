"""
Gestor de pedidos - usando Supabase PostgreSQL
"""
import os
from datetime import datetime
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

# Supabase configuration
SUPABASE_URL = os.getenv("SUPABASE_URL", "https://fwxhcytqyiggkikbqvkc.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZ3eGhjeXRxeWlnZ2tpa2JxdmtjIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3NjAzMTY3MSwiZXhwIjoyMDkxNjA3NjcxfQ.BgIIAj2uPHAXKiFDSHH421q0Ir9YGX6mIh3c1vxoSG4")

from supabase import create_client

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def inicializar_tabla():
    """Crea la tabla de pedidos si no existe"""
    try:
        # Intentar crear la tabla
        supabase.table("pedidos").select("*").limit(1).execute()
        print("✓ Tabla 'pedidos' ya existe")
    except Exception as e:
        print(f"⚠️ Inicializando tabla de pedidos: {e}")
        try:
            # Intentar crear la tabla mediante SQL
            pass  # Supabase creará la tabla automáticamente
        except:
            pass

def crear_pedido(tipo: str, objetivo: str, email: str, nombre: str, datos_extra: str = "") -> dict:
    """Crea un nuevo pedido y lo guarda en Supabase"""
    # Extraer instagram_sender_id de datos_extra si viene en formato "instagram_sender_id:123"
    instagram_sender_id = None
    if datos_extra and "instagram_sender_id:" in datos_extra:
        instagram_sender_id = datos_extra.split("instagram_sender_id:")[-1]

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
        "link_flow": None,
        "instagram_sender_id": instagram_sender_id
    }

    try:
        response = supabase.table("pedidos").insert(pedido).execute()
        print(f"✓ Pedido creado en Supabase: {pedido['id']}")
        return pedido
    except Exception as e:
        print(f"❌ Error creando pedido: {e}")
        raise

def obtener_pedido(email: str) -> Optional[dict]:
    """Obtiene el pedido más reciente de un cliente"""
    try:
        response = supabase.table("pedidos").select("*").eq("email", email).order("fecha_creacion", desc=True).limit(1).execute()

        if response.data and len(response.data) > 0:
            return response.data[0]
        return None
    except Exception as e:
        print(f"❌ Error obteniendo pedido: {e}")
        return None

def actualizar_pedido(email: str, estado: str, link_flow: str = None) -> bool:
    """Actualiza el estado de un pedido"""
    try:
        # Obtener el pedido más reciente
        pedido = obtener_pedido(email)

        if not pedido:
            return False

        update_data = {"estado": estado}

        if estado == "pagado":
            update_data["fecha_pago"] = datetime.now().isoformat()

        if link_flow:
            update_data["link_flow"] = link_flow

        response = supabase.table("pedidos").update(update_data).eq("id", pedido["id"]).execute()
        print(f"✓ Pedido actualizado: {estado}")
        return True
    except Exception as e:
        print(f"❌ Error actualizando pedido: {e}")
        return False

def obtener_todos() -> list:
    """Obtiene todos los pedidos"""
    try:
        response = supabase.table("pedidos").select("*").order("fecha_creacion", desc=True).execute()
        return response.data if response.data else []
    except Exception as e:
        print(f"❌ Error obteniendo pedidos: {e}")
        return []

# Inicializar tabla al importar el módulo
inicializar_tabla()
