# Configuración de Flow.com - Modo Manual

Este proyecto usa **links de pago manuales de Flow.com** para generar informes automáticamente.

---

## 🎯 Flujo de Uso

```
1. TÚ generas link en Flow.com (una sola vez)
   ↓
2. CLIENTE paga en el link
   ↓
3. FLOW envía webhook automáticamente a tu API
   ↓
4. API GENERA PDF automáticamente
   ↓
5. CLIENTE RECIBE email con PDF
```

---

## ⚙️ Paso 1: Generar Link de Pago en Flow.com

### En Flow.com Dashboard:

1. Ve a **"Link de pago"** (menú izquierdo)
2. Haz clic en **"Crear nuevo link"** (o similar)
3. Ingresa:
   - **Monto**: 
     - Due Diligence: $29.990
     - Mercado: $19.990
     - Persona: $9.990
     - Competencia: $24.990
   - **Descripción**: "Informe [tipo] - [empresa/persona]"
   - **Email cliente**: el email del cliente

4. Haz clic en **"Generar link"**
5. **Copia el link** y envíalo al cliente por WhatsApp, email, etc.

---

## 📡 Paso 2: Configurar Webhook

Cuando el cliente pague, Flow enviará automáticamente un webhook a:

```
POST https://web-production-e421.up.railway.app/webhook/flow
```

**¿Dónde lo configuro?**

En Flow.com → **Configuración** → **Datos de integración** (o similar)
- Busca: "Webhook URL" o "Notificaciones"
- Ingresa: `https://web-production-e421.up.railway.app/webhook/flow`
- **Guarda**

---

## 🔄 Paso 3: El Sistema Funciona Automáticamente

Una vez configurado:

1. Cliente paga en el link ✅
2. Flow envía webhook a tu API 🔔
3. Tu API:
   - Recibe los datos del cliente
   - Investiga con Claude AI 🤖
   - Genera PDF del informe 📄
   - Envía email con PDF 📧

**Todo automático.**

---

## 📊 Datos que Recibe el Webhook

Cuando Flow envía el webhook, incluye:

```json
{
  "status": "paid",
  "payer_email": "cliente@example.com",
  "payer_name": "Juan",
  "flowOrder": "123456",
  "metadata": {
    "tipo": "due_diligence",
    "objetivo": "Empresa XYZ",
    "datos_extra": "..."
  }
}
```

---

## 🧪 Testear el Webhook

Para probar que funciona:

```bash
curl -X POST https://web-production-e421.up.railway.app/webhook/flow \
  -H "Content-Type: application/json" \
  -d '{
    "status": "paid",
    "payer_email": "test@test.com",
    "payer_name": "Test User",
    "flowOrder": "999999",
    "metadata": {
      "tipo": "due_diligence",
      "objetivo": "Empresa Test",
      "datos_extra": ""
    }
  }'
```

Deberías ver el PDF generado en `output_pdfs/` y un log en Railway.

---

## 📋 Precios Recomendados

| Tipo de Informe | Precio |
|---|---|
| **Due Diligence** (empresas) | $29.990 |
| **Análisis de Mercado** | $19.990 |
| **Investigación de Persona** | $9.990 |
| **Inteligencia Competitiva** | $24.990 |

---

## ✅ Checklist de Configuración

- [ ] Cuenta en Flow.com creada y activa
- [ ] Webpay Plus configurado en Flow
- [ ] Variables de entorno en Railway:
  - [ ] `ANTHROPIC_API_KEY` ✅
  - [ ] `FLOW_SECRET_KEY` ✅
- [ ] Link de pago generado en Flow
- [ ] Webhook URL configurado en Flow.com
- [ ] Probado con curl o cliente de prueba

---

## 🚀 En Producción

1. **Crear un formulario web** (HTML simple) donde el cliente ingrese:
   - Tipo de informe
   - Empresa/persona a investigar
   - Email
   - Nombre

2. **Tú generas el link** en Flow basado en esos datos

3. **Envías el link** al cliente automáticamente

---

## 📞 Soporte

Si el webhook no funciona:

1. Revisa los logs en Railway:
   ```bash
   railway logs --tail
   ```

2. Verifica que la URL del webhook sea exacta

3. Prueba con curl (comando arriba)

---

**¡Listo!** El sistema está operativo. 🎉
