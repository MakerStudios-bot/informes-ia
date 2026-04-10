# Deploy en Railway

## Requisitos Previos

1. **Cuenta en Railway.app** - Crea una en https://railway.app
2. **CLI de Railway** - Instala con: `npm install -g @railway/cli`
3. **Git** - Versión control para el código
4. **Cuenta de GitHub** - Para conectar el repositorio

---

## Paso 1: Inicializar Git Repository

```bash
cd /Users/macbookpro/informes-ia

# Inicializar git
git init
git add .
git commit -m "Initial commit: Informes IA pipeline"

# Conectar a GitHub (crear repo en github.com primero)
git remote add origin https://github.com/TU_USUARIO/informes-ia.git
git branch -M main
git push -u origin main
```

---

## Paso 2: Conectarse a Railway

```bash
# Login a Railway
railway login

# Crear nuevo proyecto
railway init
# Selecciona: Create new project
# Nombre: informes-ia
```

---

## Paso 3: Configurar Variables de Entorno en Railway

```bash
# Configura las variables de entorno en Railway
railway variables set ANTHROPIC_API_KEY=sk-ant-api03-...
railway variables set ENVIRONMENT=production
railway variables set FLOW_SECRET=tu_secret_key_aqui
```

O en el dashboard:
1. Ve a https://railway.app/dashboard
2. Selecciona tu proyecto "informes-ia"
3. Ve a "Variables"
4. Agrega:
   - `ANTHROPIC_API_KEY`: Tu API key de Anthropic
   - `ENVIRONMENT`: `production`
   - `FLOW_SECRET`: Tu secret de Flow (si usas)

---

## Paso 4: Deploy

```bash
# Opción A: Deploy desde CLI
railway up

# Opción B: Deploy desde Dashboard (automático)
# Railway detectará Procfile y railway.toml automáticamente
```

Railway asignará automáticamente un puerto y lo mapeará a través de `$PORT`.

---

## Paso 5: Verificar Deploy

```bash
# Ver logs en tiempo real
railway logs

# Ver URL pública de tu servicio
railway domain

# Probar health check
curl https://tu-dominio.up.railway.app/

# Respuesta esperada:
# {"status":"ok"}
```

---

## Estructura de Deploy

```
Procfile          ← Le dice a Railway cómo ejecutar la app
railway.toml      ← Configuración de Railway
requirements.txt  ← Dependencias Python (detectadas automáticamente)
main.py           ← App FastAPI principal
pipeline.py       ← Pipeline de generación de informes
modules/          ← Módulos (researcher, writer, pdf_generator, mailer)
output_pdfs/      ← Carpeta para PDFs generados
```

---

## Webhook Flow Integration

Una vez deployado, tu URL webhook es:
```
POST https://tu-dominio.up.railway.app/webhook/flow
```

Configúrala en tu dashboard de Flow.com:
1. Settings → Webhooks
2. URL: `https://tu-dominio.up.railway.app/webhook/flow`
3. Headers: `Authorization: Bearer <FLOW_SECRET>`

---

## Troubleshooting

**Error: `ModuleNotFoundError`**
```bash
railway logs  # Ver logs
# Verificar que todas las importaciones en requirements.txt estén
```

**Error: `OSError: cannot load library 'gobject'`**
- Ya resuelto: usamos fpdf2 en lugar de weasyprint

**Puerto no responde**
```bash
# Verificar que usa $PORT
railway variables list
railway logs
```

**PDFs no se generan**
- Verificar `output_pdfs/` tiene permisos de escritura
- Railway usa un filesystem efímero: los PDFs se pierden al reiniciar
- Solución: guardar en base de datos o S3 (próxima iteración)

---

## Monitoreo en Railway

1. **Logs**: `railway logs --tail`
2. **Métricas**: Dashboard → Deployments
3. **Alertas**: Settings → Monitoring

---

## Actualizar después de cambios

```bash
git add .
git commit -m "Update: [descripción del cambio]"
git push origin main

# Railway detecta el push y redeploya automáticamente
# Si usas CLI:
railway up
```

---

## Costos

Railway es **gratuito hasta $5 USD/mes** de uso. Este proyecto consume muy poco.

Para más detalles: https://railway.app/pricing
