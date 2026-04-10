import os, base64
from pathlib import Path

async def send_report(email, nombre, tipo_label, objetivo, pdf_path):
    # Por ahora solo imprime — activar Resend cuando tengas la API key
    print(f"  [MAIL SIMULADO] Enviando a {email} — adjunto: {pdf_path}")
