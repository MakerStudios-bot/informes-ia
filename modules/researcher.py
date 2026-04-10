import os
from dotenv import load_dotenv
import anthropic

load_dotenv()
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

PROMPTS = {
    "due_diligence": "Investiga esta empresa: {objetivo}. Busca: datos corporativos, reputación, noticias, red flags. Sé conciso.",
    "mercado": "Analiza este mercado: {objetivo}. Investiga: competidores, precios, tendencias.",
    "persona": "Información pública de: {objetivo}. Cargos, empresas, menciones en medios.",
    "competencia": "Analiza este competidor: {objetivo}. Propuesta de valor, precios, estrategia digital.",
}

async def research(tipo: str, objetivo: str, datos_extra: str = "") -> dict:
    prompt = PROMPTS.get(tipo, PROMPTS["due_diligence"]).format(objetivo=objetivo)
    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=2000,
        tools=[{"type": "web_search_20250305", "name": "web_search"}],
        messages=[{"role": "user", "content": prompt}],
    )
    texto = "".join(b.text for b in response.content if b.type == "text")
    return {"tipo": tipo, "objetivo": objetivo, "hallazgos_raw": texto}
