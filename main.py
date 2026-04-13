"""
Informes IA — Servidor principal
"""
import os, hmac, hashlib
from fastapi import FastAPI, Request, HTTPException, BackgroundTasks, Form
from fastapi.responses import JSONResponse, FileResponse, HTMLResponse
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
# Redeploy - API key balance verified

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

@app.get("/test", response_class=HTMLResponse)
async def test_page():
    """Página de test para crear y listar pedidos"""
    html = """
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Test - Crear Pedido</title>
        <style>
            body { font-family: monospace; max-width: 800px; margin: 50px auto; background: #1e1e1e; color: #d4d4d4; padding: 20px; }
            .form-group { margin: 15px 0; }
            input, select, textarea { width: 100%; padding: 10px; margin-top: 5px; background: #2d2d2d; color: #d4d4d4; border: 1px solid #444; border-radius: 4px; font-family: monospace; }
            button { padding: 10px 20px; background: #0e639c; color: white; border: none; cursor: pointer; border-radius: 4px; width: 100%; }
            button:hover { background: #1177bb; }
            .log { background: #2d2d2d; padding: 15px; border-radius: 4px; margin-top: 20px; max-height: 400px; overflow-y: auto; border: 1px solid #444; }
            .log-entry { margin: 5px 0; padding: 5px; border-left: 2px solid #666; padding-left: 10px; }
            .log-entry.success { border-left-color: #4ec9b0; color: #4ec9b0; }
            .log-entry.error { border-left-color: #f48771; color: #f48771; }
            .log-entry.info { border-left-color: #9cdcfe; color: #9cdcfe; }
            h1 { color: #4ec9b0; margin-bottom: 30px; }
        </style>
    </head>
    <body>
        <h1>🔍 Test: Crear Pedido en Supabase</h1>

        <div class="form-group">
            <label>Nombre *</label>
            <input type="text" id="nombre" value="Test Usuario" required>
        </div>

        <div class="form-group">
            <label>Email *</label>
            <input type="email" id="email" value="test-nuevo@example.com" required>
        </div>

        <div class="form-group">
            <label>Tipo *</label>
            <select id="tipo" required>
                <option value="">Selecciona...</option>
                <option value="Due Diligence">Due Diligence</option>
                <option value="Análisis de Mercado">Análisis de Mercado</option>
            </select>
        </div>

        <div class="form-group">
            <label>Objetivo *</label>
            <input type="text" id="objetivo" value="Test desde navegador" required>
        </div>

        <div class="form-group">
            <label>Datos Extra</label>
            <textarea id="datos_extra" rows="3">Test de formulario</textarea>
        </div>

        <button onclick="crearPedido()">Crear Pedido</button>

        <h2 style="margin-top: 30px; color: #4ec9b0;">📋 Log de Ejecución:</h2>
        <div class="log" id="logContainer"></div>

        <h2 style="margin-top: 30px; color: #4ec9b0;">📊 Pedidos Actuales:</h2>
        <button onclick="cargarPedidos()" style="margin-bottom: 10px;">Actualizar lista</button>
        <div class="log" id="pedidosContainer"></div>

        <script>
            function addLog(mensaje, tipo = 'info') {
                const log = document.getElementById('logContainer');
                const entry = document.createElement('div');
                entry.className = `log-entry ${tipo}`;
                const timestamp = new Date().toLocaleTimeString();
                entry.textContent = `[${timestamp}] ${mensaje}`;
                log.appendChild(entry);
                log.scrollTop = log.scrollHeight;
            }

            async function crearPedido() {
                const nombre = document.getElementById('nombre').value;
                const email = document.getElementById('email').value;
                const tipo = document.getElementById('tipo').value;
                const objetivo = document.getElementById('objetivo').value;
                const datos_extra = document.getElementById('datos_extra').value;

                addLog('📤 Iniciando envío...', 'info');
                addLog(`Datos: nombre=${nombre}, email=${email}, tipo=${tipo}`, 'info');

                try {
                    const formData = new FormData();
                    formData.append('nombre', nombre);
                    formData.append('email', email);
                    formData.append('tipo', tipo);
                    formData.append('objetivo', objetivo);
                    formData.append('datos_extra', datos_extra);

                    addLog('🔗 POST a /api/pedidos', 'info');

                    const response = await fetch('/api/pedidos', {
                        method: 'POST',
                        body: formData
                    });

                    addLog(`Status: ${response.status}`, 'info');

                    const result = await response.json();

                    if (result.ok || result.pedido) {
                        addLog(`✅ Pedido creado! ID: ${result.pedido.id}`, 'success');
                        addLog(`Email: ${result.pedido.email}`, 'success');

                        setTimeout(() => {
                            cargarPedidos();
                        }, 1000);
                    } else {
                        addLog(`❌ Error: ${result.error}`, 'error');
                    }
                } catch (error) {
                    addLog(`❌ Error: ${error.message}`, 'error');
                }
            }

            async function cargarPedidos() {
                addLog('📥 Cargando lista de pedidos...', 'info');
                const container = document.getElementById('pedidosContainer');
                container.innerHTML = '<div class="log-entry info">Cargando...</div>';

                try {
                    const response = await fetch('/api/pedidos');
                    const result = await response.json();

                    if (result.ok && result.pedidos) {
                        container.innerHTML = '';
                        addLog(`✅ Se encontraron ${result.pedidos.length} pedidos`, 'success');

                        result.pedidos.forEach((pedido, i) => {
                            const entry = document.createElement('div');
                            entry.className = 'log-entry info';
                            entry.innerHTML = `
                                <strong>#${i + 1}</strong> |
                                ${pedido.nombre} (${pedido.email}) |
                                ${pedido.tipo} |
                                Estado: <strong>${pedido.estado}</strong>
                            `;
                            container.appendChild(entry);
                        });
                    } else {
                        addLog('❌ Error al cargar pedidos', 'error');
                    }
                } catch (error) {
                    addLog(`❌ Error: ${error.message}`, 'error');
                }
            }

            window.addEventListener('load', () => {
                addLog('🚀 Test iniciado', 'info');
                cargarPedidos();
            });
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html)

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
    tipo: str = Form(...),
    objetivo: str = Form(...),
    email: str = Form(...),
    nombre: str = Form(...),
    datos_extra: str = Form(""),
    background_tasks: BackgroundTasks = None
):
    """API para crear un pedido desde el dashboard"""
    try:
        print("Creando pedido:", nombre, email)
        pedido = crear_pedido(tipo, objetivo, email, nombre, datos_extra)
        print("Pedido creado:", pedido.get('id'))

        # Enviar notificación al dueño
        if background_tasks:
            print("Notificando al dueño...")
            background_tasks.add_task(notify_new_order, email, nombre, tipo, objetivo, datos_extra)

        return JSONResponse({
            "ok": True,
            "pedido": pedido
        })
    except Exception as e:
        print("Error creando pedido:", str(e))
        import traceback
        traceback.print_exc()
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
