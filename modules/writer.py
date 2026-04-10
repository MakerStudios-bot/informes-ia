import os
from datetime import datetime
from dotenv import load_dotenv
import anthropic

load_dotenv()
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

PROMPT_WRITER = """Eres un redactor de informes profesionales.
Con estos hallazgos de investigación:
---
{hallazgos}
---
Redacta un informe profesional completo en HTML.
Usa estas clases CSS: .section, .section-title, .highlight, .alert, .tag-positive, .tag-negative, .tag-neutral
Si no hay datos sobre algo, escribe: "No se encontró información pública disponible."
Incluye una sección final de Conclusión y recomendación.
Devuelve SOLO el HTML del cuerpo (sin html/head tags)."""

async def write_report(tipo, tipo_label, objetivo, datos, nombre_cliente="") -> str:
    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=2000,
        messages=[{"role": "user", "content": PROMPT_WRITER.format(hallazgos=datos["hallazgos_raw"])}],
    )
    contenido = response.content[0].text
    fecha = datetime.now().strftime("%d de %B de %Y")
    return f"""<!DOCTYPE html><html lang="es"><head><meta charset="UTF-8">
<style>
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{ font-family: 'Helvetica Neue', Arial, sans-serif; color:#1a1a1a; font-size:14px; line-height:1.7; }}
.cover {{ background:#0f1117; color:white; padding:60px 50px; }}
.cover-label {{ font-size:11px; letter-spacing:.15em; text-transform:uppercase; color:#6b7280; margin-bottom:12px; }}
.cover-title {{ font-size:28px; font-weight:600; margin-bottom:8px; }}
.cover-objetivo {{ font-size:15px; color:#9ca3af; margin-bottom:30px; }}
.cover-meta {{ display:flex; gap:40px; font-size:12px; color:#6b7280; border-top:1px solid #1f2937; padding-top:20px; }}
.cover-meta strong {{ color:#d1d5db; display:block; }}
.body {{ padding:40px 50px; }}
.section {{ margin-bottom:36px; }}
.section-title {{ font-size:16px; font-weight:600; border-bottom:2px solid #e5e7eb; padding-bottom:8px; margin-bottom:16px; }}
.section p {{ margin-bottom:10px; color:#374151; }}
.section ul {{ margin:10px 0 10px 20px; color:#374151; }}
.section ul li {{ margin-bottom:6px; }}
.highlight {{ background:#f0f9ff; border-left:3px solid #0284c7; padding:12px 16px; margin:12px 0; }}
.alert {{ background:#fff7ed; border-left:3px solid #f59e0b; padding:12px 16px; margin:12px 0; }}
.tag-positive {{ display:inline-block; background:#dcfce7; color:#166534; font-size:11px; padding:3px 10px; border-radius:20px; margin:2px; }}
.tag-negative {{ display:inline-block; background:#fee2e2; color:#991b1b; font-size:11px; padding:3px 10px; border-radius:20px; margin:2px; }}
.tag-neutral {{ display:inline-block; background:#f3f4f6; color:#374151; font-size:11px; padding:3px 10px; border-radius:20px; margin:2px; }}
.footer {{ background:#f9fafb; border-top:1px solid #e5e7eb; padding:20px 50px; font-size:11px; color:#9ca3af; display:flex; justify-content:space-between; }}
</style></head><body>
<div class="cover">
  <div class="cover-label">Informe de inteligencia</div>
  <div class="cover-title">{tipo_label}</div>
  <div class="cover-objetivo">{objetivo}</div>
  <div class="cover-meta">
    <span><strong>Fecha</strong>{fecha}</span>
    <span><strong>Solicitado por</strong>{nombre_cliente or "Cliente"}</span>
    <span><strong>Generado por</strong>Informes IA</span>
  </div>
</div>
<div class="body">{contenido}</div>
<div class="footer"><span>Informe generado con IA a partir de fuentes públicas.</span><span>informes-ia.cl</span></div>
</body></html>"""
