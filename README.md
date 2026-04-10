# 📊 Informes IA

Servicio de generación de informes de inteligencia empresarial automatizados con IA.

Genera reportes profesionales en PDF usando búsqueda web y Claude AI.

## ✨ Características

- 🔍 **Investigación Automática**: Búsqueda web integrada con Claude
- 📄 **Generación de Informes**: HTML → PDF profesional
- 🚀 **Webhook Ready**: Integración con Flow.com para pagos
- 📧 **Email Automático**: Envío de informes (simulado/Resend)
- 📦 **Escalable**: Listo para Railway, Docker, etc.

## 📋 Tipos de Informes

| Tipo | Descripción |
|------|-------------|
| `due_diligence` | Análisis de riesgo empresarial |
| `mercado` | Análisis de mercado y tendencias |
| `persona` | Investigación de personas públicas |
| `competencia` | Inteligencia competitiva |

## 🚀 Quick Start (Local)

```bash
# 1. Clonar y entrar
cd informes-ia

# 2. Crear venv
python3 -m venv venv
source venv/bin/activate

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Configurar .env
ANTHROPIC_API_KEY=sk-ant-...

# 5. Ejecutar test
python test_pipeline.py

# 6. Ver PDF
open output_pdfs/*.pdf
```

## 📡 API Endpoints

### Health Check
```bash
GET /
```
Respuesta:
```json
{"status": "ok"}
```

### Webhook Flow (Pagos)
```bash
POST /webhook/flow
```
Body:
```json
{
  "status": "paid",
  "payer_email": "cliente@example.com",
  "payer_name": "Juan",
  "flowOrder": "123456",
  "metadata": {
    "tipo": "due_diligence",
    "objetivo": "Empresa XYZ",
    "datos_extra": "Información adicional"
  }
}
```

## 🏗️ Arquitectura

```
main.py              ← FastAPI server + webhook
  └─ pipeline.py    ← Orquestación del flujo
      ├─ researcher.py   ← Búsqueda web + análisis con Claude
      ├─ writer.py       ← Redacción de informe
      ├─ pdf_generator.py ← Conversión a PDF
      └─ mailer.py       ← Envío de email
```

## 🔧 Variables de Entorno

```bash
ANTHROPIC_API_KEY=sk-ant-...          # API key de Anthropic
PORT=8000                              # Puerto (Railway asigna automáticamente)
ENVIRONMENT=development|production     # Entorno
FLOW_SECRET=tu_secret_key              # Para validar webhooks de Flow
```

## 📦 Dependencias Principales

- **FastAPI**: Framework web asincrónico
- **Anthropic**: Claude API para IA
- **fpdf2**: Generación de PDFs
- **python-dotenv**: Variables de entorno

## 🚂 Deploy en Railway

Ver [DEPLOY.md](./DEPLOY.md) para instrucciones completas.

Quick deploy:
```bash
railway login
railway init
railway variables set ANTHROPIC_API_KEY=sk-ant-...
railway up
```

## 📝 Ejemplo de Uso

```python
import asyncio
from pipeline import run_pipeline

async def main():
    pedido = {
        "tipo": "due_diligence",
        "objetivo": "Empresa Falabella S.A.",
        "email": "cliente@example.com",
        "nombre": "Juan",
        "datos_extra": ""
    }
    await run_pipeline(pedido)

asyncio.run(main())
```

## 🧪 Testing

```bash
# Ejecutar test del pipeline completo
python test_pipeline.py

# Ver PDF generado
ls output_pdfs/
```

## 🔐 Seguridad

- ✅ Variables sensibles en .env (no en código)
- ✅ HMAC validation para webhooks (pendiente implementar)
- ✅ Rate limiting en Claude API
- ✅ Validación de entrada en webhook

## 📊 Flujo de Generación

```
1. Webhook recibe pedido pagado
2. Extrae: tipo, objetivo, datos_extra
3. Investigación: web_search + Claude
4. Redacción: HTML profesional
5. PDF: Conversión y almacenamiento
6. Email: Envío al cliente
```

## 🐛 Troubleshooting

**Error: Rate limit exceeded**
- Railway → Variables → ANTHROPIC_API_KEY (verificar que sea válida)
- Cambiar a Haiku si es muy lento

**PDF vacío**
- Verificar output_pdfs/ existe
- Revisar logs: `railway logs`

**Webhook no recibe datos**
- Verificar FLOW_SECRET en variables
- Revisar URL exacta en Flow.com

## 📚 Documentación

- [Anthropic Claude API](https://docs.anthropic.com)
- [FastAPI](https://fastapi.tiangolo.com)
- [Railway Deployment](https://docs.railway.app)
- [Flow.com](https://flow.com)

## 🤝 Contribuciones

Mejoras bienvenidas. Próximas features:

- [ ] Almacenamiento en S3
- [ ] Base de datos para historial
- [ ] Panel de administración
- [ ] Más tipos de informes
- [ ] Generación de reportes en Excel
- [ ] Integración con Zapier

## 📄 Licencia

MIT

---

**Generado con IA.** ¿Preguntas? Revisar DEPLOY.md o TROUBLESHOOTING.
