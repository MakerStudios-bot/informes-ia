"""
Script de prueba para simular un pago en Flow y verificar todo el flujo
"""
import json
import httpx
import asyncio
from datetime import datetime

async def test_full_flow():
    """Prueba el flujo completo: crear pedido → simular pago → generar informe"""

    SERVER_URL = "http://localhost:8000"

    print("=" * 60)
    print("🧪 PRUEBA DEL FLUJO COMPLETO DE INFORMES-IA")
    print("=" * 60)

    # 1. Crear un pedido
    print("\n1️⃣  Creando un pedido...")
    pedido_data = {
        "tipo": "due_diligence",
        "objetivo": "Empresa Test SPA",
        "email": "test@example.com",
        "nombre": "Cliente Test",
        "datos_extra": "Prueba desde script"
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{SERVER_URL}/api/pedidos",
            params=pedido_data
        )

    if response.status_code != 200:
        print(f"❌ Error creando pedido: {response.text}")
        return

    pedido = response.json()["pedido"]
    print(f"✅ Pedido creado: {pedido['id']}")
    print(f"   Email: {pedido['email']}")
    print(f"   Tipo: {pedido['tipo']}")

    # 2. Simular webhook de pago
    print(f"\n2️⃣  Simulando pago en Flow...")
    webhook_data = {
        "status": "paid",
        "payer_email": pedido["email"],
        "flowOrder": 123456789,
        "amount": 29990
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{SERVER_URL}/webhook/flow",
            json=webhook_data
        )

    if response.status_code != 200:
        print(f"❌ Error en webhook: {response.text}")
        return

    print(f"✅ Webhook enviado (status=paid)")
    print(f"   Flow está procesando en background...")

    # 3. Esperar a que se genere
    print(f"\n3️⃣  Esperando generación del informe (5 segundos)...")
    await asyncio.sleep(5)

    # 4. Verificar estado
    print(f"\n4️⃣  Verificando estado del pedido...")
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{SERVER_URL}/api/pedidos")

    if response.status_code == 200:
        pedidos = response.json()["pedidos"]
        pedido_updated = next(
            (p for p in pedidos if p["email"] == pedido["email"]),
            None
        )

        if pedido_updated:
            print(f"✅ Estado actual: {pedido_updated['estado']}")
            if pedido_updated["estado"] == "pagado":
                print(f"   📧 El informe debería haberse enviado por email")
            print(f"   Fecha de pago: {pedido_updated['fecha_pago']}")
        else:
            print("❌ Pedido no encontrado")
    else:
        print(f"❌ Error obteniendo pedidos: {response.text}")

    print("\n" + "=" * 60)
    print("✨ Prueba completada!")
    print("=" * 60)
    print("\nPasos siguientes:")
    print("1. Configura el webhook real en Flow.cl:")
    print("   URL: https://informes-ia.up.railway.app/webhook/flow")
    print("2. Realiza un pago real para verificar que funciona")
    print("=" * 60)

if __name__ == "__main__":
    print("⚠️  Asegúrate de que el servidor está corriendo en localhost:8000")
    print("   Ejecuta: uvicorn main:app --reload")
    print()
    asyncio.run(test_full_flow())
