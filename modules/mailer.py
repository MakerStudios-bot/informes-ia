import os
import base64
from pathlib import Path
from dotenv import load_dotenv
import httpx

load_dotenv()

RESEND_API_KEY = os.getenv("RESEND_API_KEY", "")
RESEND_API_URL = "https://api.resend.com/emails"
FROM_EMAIL = "neurox.contacto@gmail.com"
OWNER_EMAIL = os.getenv("OWNER_EMAIL", "contacto@neurox.agency")

async def send_report(email: str, nombre: str, tipo_label: str, objetivo: str, pdf_path: str):
    """
    Envía el informe generado por email usando Resend.

    Args:
        email: Email del cliente
        nombre: Nombre del cliente
        tipo_label: Tipo de informe (ej: "Due Diligence de Empresa")
        objetivo: Empresa/persona investigada
        pdf_path: Ruta al archivo PDF
    """
    if not RESEND_API_KEY:
        print(f"  [MAIL SIMULADO] Enviando a {email} — adjunto: {pdf_path}")
        print("  ⚠️  RESEND_API_KEY no configurada. Configúrala en Railway para envíos reales.")
        return

    try:
        # Leer el PDF
        pdf_file = Path(pdf_path)
        if not pdf_file.exists():
            print(f"  ❌ PDF no encontrado: {pdf_path}")
            return

        with open(pdf_file, "rb") as f:
            pdf_data = base64.b64encode(f.read()).decode()

        # Preparar email
        subject = f"Tu Informe: {tipo_label} - {objetivo}"
        html_body = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 8px; }}
                .content {{ margin: 20px 0; }}
                .footer {{ color: #999; font-size: 12px; margin-top: 30px; border-top: 1px solid #ddd; padding-top: 20px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>📊 Tu Informe Está Listo</h1>
                </div>

                <div class="content">
                    <p>¡Hola {nombre}!</p>
                    <p>Tu <strong>{tipo_label}</strong> para <strong>{objetivo}</strong> ha sido generado exitosamente.</p>
                    <p>El PDF se encuentra adjunto en este email.</p>

                    <h3>Contenido del Informe:</h3>
                    <ul>
                        <li>Datos corporativos</li>
                        <li>Desempeño financiero</li>
                        <li>Análisis de riesgos</li>
                        <li>Conclusiones y recomendaciones</li>
                    </ul>

                    <p>Si tienes preguntas, contáctanos.</p>
                </div>

                <div class="footer">
                    <p>Informe generado automáticamente con IA</p>
                    <p>© 2026 Informes IA - informes-ia.cl</p>
                </div>
            </div>
        </body>
        </html>
        """

        # Enviar con Resend usando httpx (async)
        headers = {
            "Authorization": f"Bearer {RESEND_API_KEY}",
            "Content-Type": "application/json"
        }

        payload = {
            "from": FROM_EMAIL,
            "to": email,
            "subject": subject,
            "html": html_body,
            "attachments": [
                {
                    "filename": pdf_file.name,
                    "content": pdf_data,
                    "encoding": "base64"
                }
            ]
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(RESEND_API_URL, json=payload, headers=headers, timeout=10)

        if response.status_code == 200:
            print(f"  ✅ Email enviado a {email}")
            return True
        else:
            print(f"  ❌ Error enviando email: {response.text}")
            return False

    except Exception as e:
        print(f"  ❌ Error en mailer: {e}")
        return False

async def notify_new_order(email: str, nombre: str, tipo: str, objetivo: str, datos_extra: str = ""):
    """Notifica al dueño cuando llega un nuevo pedido"""
    if not RESEND_API_KEY or not OWNER_EMAIL:
        print(f"  ⚠️  No se puede enviar notificación (falta OWNER_EMAIL)")
        return

    try:
        html_body = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 8px; }}
                .content {{ margin: 20px 0; }}
                .field {{ margin: 12px 0; padding: 10px; background: #f5f5f5; border-radius: 4px; }}
                .label {{ font-weight: bold; color: #667eea; }}
                .button {{ display: inline-block; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 12px 24px; border-radius: 4px; text-decoration: none; margin-top: 20px; }}
                .footer {{ color: #999; font-size: 12px; margin-top: 30px; border-top: 1px solid #ddd; padding-top: 20px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>📬 Nuevo Pedido Recibido</h1>
                </div>

                <div class="content">
                    <p>Hola,</p>
                    <p>Se ha recibido un nuevo pedido que requiere tu confirmación.</p>

                    <div class="field">
                        <div class="label">Cliente:</div>
                        {nombre}
                    </div>

                    <div class="field">
                        <div class="label">Email:</div>
                        {email}
                    </div>

                    <div class="field">
                        <div class="label">Tipo de Informe:</div>
                        {tipo}
                    </div>

                    <div class="field">
                        <div class="label">Sobre:</div>
                        {objetivo}
                    </div>

                    {f'<div class="field"><div class="label">Notas:</div>{datos_extra}</div>' if datos_extra else ''}

                    <a href="https://web-production-e421.up.railway.app/dashboard" class="button">Ver en Dashboard →</a>

                    <p style="margin-top: 20px;">Haz clic en el botón de arriba para ir al dashboard y confirmar el pago.</p>
                </div>

                <div class="footer">
                    <p>Este es un pedido de Informes IA</p>
                </div>
            </div>
        </body>
        </html>
        """

        headers = {
            "Authorization": f"Bearer {RESEND_API_KEY}",
            "Content-Type": "application/json"
        }

        payload = {
            "from": FROM_EMAIL,
            "to": OWNER_EMAIL,
            "subject": f"📬 Nuevo Pedido: {tipo} - {objetivo}",
            "html": html_body,
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(RESEND_API_URL, json=payload, headers=headers, timeout=10)

        if response.status_code == 200:
            print(f"  ✅ Notificación enviada a {OWNER_EMAIL}")
            return True
        else:
            print(f"  ⚠️  Error enviando notificación: {response.text}")
            return False

    except Exception as e:
        print(f"  ⚠️  Error en notify_new_order: {e}")
        return False
