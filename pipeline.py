import asyncio
import httpx
import os
from datetime import datetime
from dotenv import load_dotenv
from modules.researcher import research
from modules.writer import write_report
from modules.pdf_generator import generate_pdf
from modules.mailer import send_report

load_dotenv()

NEUROX_BOT_URL = os.getenv("NEUROX_BOT_URL", "http://localhost:5000")

TIPOS = {
    "due_diligence": "Due Diligence de Empresa",
    "mercado": "Análisis de Mercado",
    "persona": "Investigación de Persona",
    "competencia": "Inteligencia Competitiva",
}

async def notify_neurox_bot(instagram_sender_id: str, pdf_filename: str, objetivo: str):
    """Notifica al bot de Neurox cuando el PDF está listo"""
    try:
        pdf_url = f"https://web-production-e421.up.railway.app/pdf/{pdf_filename}"
        payload = {
            "instagram_sender_id": instagram_sender_id,
            "pdf_url": pdf_url,
            "objetivo": objetivo
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{NEUROX_BOT_URL}/notify-pdf",
                json=payload,
                timeout=10
            )

        if response.status_code == 200:
            print(f"✅ Notificación enviada a Neurox bot: {instagram_sender_id}")
        else:
            print(f"⚠️ Error notificando bot: {response.status_code}")
    except Exception as e:
        print(f"⚠️ Error en notify_neurox_bot: {e}")

async def run_pipeline(pedido: dict):
    tipo_label = TIPOS.get(pedido["tipo"], pedido["tipo"])
    informe_id = f"{pedido['tipo']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    print(f"[{informe_id}] Iniciando pipeline... (API balance OK)")
    datos = await research(pedido["tipo"], pedido["objetivo"], pedido.get("datos_extra",""))
    html  = await write_report(pedido["tipo"], tipo_label, pedido["objetivo"], datos, pedido.get("nombre",""))
    pdf   = await generate_pdf(html, informe_id)
    pdf_filename = f"{informe_id}.pdf"

    await send_report(pedido["email"], pedido.get("nombre","Cliente"), tipo_label, pedido["objetivo"], pdf)

    # Si hay instagram_sender_id, notificar al bot
    instagram_sender_id = pedido.get("instagram_sender_id")
    if instagram_sender_id:
        await notify_neurox_bot(instagram_sender_id, pdf_filename, pedido["objetivo"])

    print(f"[{informe_id}] ✓ Listo")
