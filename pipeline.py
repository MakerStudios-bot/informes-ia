import asyncio
from datetime import datetime
from modules.researcher import research
from modules.writer import write_report
from modules.pdf_generator import generate_pdf
from modules.mailer import send_report

TIPOS = {
    "due_diligence": "Due Diligence de Empresa",
    "mercado": "Análisis de Mercado",
    "persona": "Investigación de Persona",
    "competencia": "Inteligencia Competitiva",
}

async def run_pipeline(pedido: dict):
    tipo_label = TIPOS.get(pedido["tipo"], pedido["tipo"])
    informe_id = f"{pedido['tipo']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    print(f"[{informe_id}] Iniciando pipeline...")
    datos = await research(pedido["tipo"], pedido["objetivo"], pedido.get("datos_extra",""))
    html  = await write_report(pedido["tipo"], tipo_label, pedido["objetivo"], datos, pedido.get("nombre",""))
    pdf   = await generate_pdf(html, informe_id)
    await send_report(pedido["email"], pedido.get("nombre","Cliente"), tipo_label, pedido["objetivo"], pdf)
    print(f"[{informe_id}] ✓ Listo")
