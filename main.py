"""
Informes IA — Servidor principal
"""
import os, hmac, hashlib
from fastapi import FastAPI, Request, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import glob
from pathlib import Path
from dotenv import load_dotenv
from pipeline import run_pipeline
from modules.pedidos_manager import crear_pedido, obtener_pedido, actualizar_pedido, obtener_todos
from modules.mailer import notify_new_order

load_dotenv()
app = FastAPI(title="Informes IA", version="1.0.0")
FLOW_SECRET = os.getenv("FLOW_SECRET", "")

@app.post("/webhook/flow")
async def webhook_flow(request: Request, background_tasks: BackgroundTasks):
    """Webhook que recibe notificaciones de pagos de Flow"""
    body = await request.body()
    data = await request.json()

    # Flow envía status="paid" cuando se completa el pago
    if data.get("status") != "paid":
        print(f"Webhook recibido pero no es pago completado: {data.get('status')}")
        return JSONResponse({"ok": True})

    email = data.get("payer_email")
    print(f"\n💰 Pago recibido de {email}")

    # Buscar el pedido en la base de datos
    pedido_guardado = obtener_pedido(email)

    if not pedido_guardado:
        print(f"❌ No se encontró pedido para {email}")
        return JSONResponse({"error": "Pedido no encontrado"}, status_code=404)

    # Actualizar estado del pedido
    actualizar_pedido(email, "pagado")
    print(f"✓ Pedido actualizado a 'pagado'")

    # Datos del pedido para generar informe
    pedido = {
        "email": pedido_guardado["email"],
        "nombre": pedido_guardado["nombre"],
        "tipo": pedido_guardado["tipo"],
        "objetivo": pedido_guardado["objetivo"],
        "datos_extra": pedido_guardado["datos_extra"],
        "flow_order": data.get("flowOrder"),
        "instagram_sender_id": pedido_guardado.get("instagram_sender_id"),
    }

    # Generar informe en background
    background_tasks.add_task(run_pipeline, pedido)
    print(f"📊 Iniciando generación de informe...")

    return JSONResponse({"ok": True})

@app.get("/")
async def landing():
    """Sirve la landing page con formulario de solicitud"""
    landing_path = Path(__file__).parent / "landing.html"
    if landing_path.exists():
        return FileResponse(landing_path)
    return JSONResponse({"error": "Landing page not found"}, status_code=404)

@app.get("/dashboard")
async def dashboard():
    """Sirve el dashboard HTML"""
    dashboard_path = Path(__file__).parent / "dashboard.html"
    if dashboard_path.exists():
        return FileResponse(dashboard_path)
    return JSONResponse({"error": "Dashboard not found"}, status_code=404)

@app.get("/pdf/{filename}")
async def get_pdf(filename: str):
    """Sirve un PDF generado públicamente"""
    # Sanitizar nombre para evitar path traversal
    if ".." in filename or filename.startswith("/"):
        return JSONResponse({"error": "Invalid filename"}, status_code=400)

    pdf_path = Path(__file__).parent / "output_pdfs" / filename
    if pdf_path.exists():
        return FileResponse(pdf_path, media_type="application/pdf")
    return JSONResponse({"error": "PDF not found"}, status_code=404)

@app.post("/api/pedidos")
async def crear_pedido_api(
    tipo: str,
    objetivo: str,
    email: str,
    nombre: str,
    datos_extra: str = "",
    background_tasks: BackgroundTasks = None
):
    """API para crear un pedido desde el dashboard"""
    try:
        pedido = crear_pedido(tipo, objetivo, email, nombre, datos_extra)

        # Enviar notificación al dueño
        if background_tasks:
            background_tasks.add_task(notify_new_order, email, nombre, tipo, objetivo, datos_extra)
        else:
            # Si no hay background_tasks disponible, intentar de forma sincrónica
            import asyncio
            asyncio.create_task(notify_new_order(email, nombre, tipo, objetivo, datos_extra))

        return JSONResponse({
            "ok": True,
            "pedido": pedido
        })
    except Exception as e:
        print(f"Error creando pedido: {e}")
        return JSONResponse({"error": str(e)}, status_code=400)

@app.get("/api/pedidos")
async def listar_pedidos():
    """API para obtener todos los pedidos"""
    try:
        pedidos = obtener_todos()
        return JSONResponse({
            "ok": True,
            "pedidos": pedidos
        })
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=400)

@app.put("/api/pedidos/{email}")
async def actualizar_link_pedido(email: str, link_flow: str):
    """API para actualizar el link de Flow de un pedido"""
    try:
        actualizar_pedido(email, "esperando_pago", link_flow)
        return JSONResponse({"ok": True})
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=400)

@app.post("/api/confirmar-pago")
async def confirmar_pago(request: Request, background_tasks: BackgroundTasks):
    """Confirma un pago manual y dispara la generación del informe"""
    try:
        data = await request.json()
        pedido_id = data.get("pedido_id")
        email = data.get("email")
        nombre = data.get("nombre")
        tipo = data.get("tipo")
        objetivo = data.get("objetivo")

        if not all([pedido_id, email, nombre, tipo, objetivo]):
            return JSONResponse({"error": "Faltan datos"}, status_code=400)

        # Obtener el pedido
        pedido_guardado = obtener_pedido(email)
        if not pedido_guardado:
            return JSONResponse({"error": "Pedido no encontrado"}, status_code=404)

        # Actualizar estado
        actualizar_pedido(email, "pagado")
        print(f"✅ Pago confirmado manualmente: {email}")

        # Preparar datos para el pipeline
        pedido = {
            "email": pedido_guardado["email"],
            "nombre": pedido_guardado["nombre"],
            "tipo": pedido_guardado["tipo"],
            "objetivo": pedido_guardado["objetivo"],
            "datos_extra": pedido_guardado["datos_extra"],
            "instagram_sender_id": pedido_guardado.get("instagram_sender_id"),
        }

        # Generar informe en background
        background_tasks.add_task(run_pipeline, pedido)
        print(f"📊 Iniciando generación de informe para {email}...")

        return JSONResponse({"ok": True, "mensaje": "Generando informe..."})
    except Exception as e:
        print(f"Error en confirmar_pago: {e}")
        return JSONResponse({"error": str(e)}, status_code=500)

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    reload = os.getenv("ENVIRONMENT", "development") == "development"
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=reload)
