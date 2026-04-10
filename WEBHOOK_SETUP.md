# Configuración Manual del Webhook de Flow

Dado que Flow.cl requiere configuración manual desde el dashboard, sigue estos pasos:

## En el Dashboard de Flow.cl

1. **Inicia sesión** en https://dashboard.flow.cl
2. **Busca la sección de Webhooks** o "Configuración de Integraciones"
3. **Agrega un nuevo webhook** con estos detalles:
   - **URL:** `https://informes-ia.up.railway.app/webhook/flow`
   - **Evento:** `payment.completed` o similar (busca el evento de "pago completado")
   - **Método:** POST
   - **Content-Type:** application/json

4. **Guarda la configuración**

## Cómo Funciona

- Flow enviará automáticamente un POST a tu webhook cada vez que un pago se complete
- El servidor en Railway recibirá la notificación en `/webhook/flow`
- Automáticamente se ejecutará:
  1. ✅ Generar el informe con Claude IA
  2. ✅ Convertir a PDF
  3. ✅ Enviar por email al cliente

## Prueba

1. Crea un pedido en tu dashboard (`https://informes-ia.up.railway.app/dashboard`)
2. Genera un link de pago en Flow
3. Realiza un pago de prueba
4. Verifica que:
   - El webhook se dispare (deberías ver logs en Railway)
   - Recibas el email con el PDF adjunto

Si no ves el evento de pago completado, contacta a Flow.cl support.
