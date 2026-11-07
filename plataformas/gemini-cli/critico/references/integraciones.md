# Integraciones externas (cargar solo si aplica)

[English](en/integrations.md).

Lee esta referencia **solo** si el artefacto toca pagos, marketplace, envíos o APIs externas. Los ejemplos usan proveedores genéricos («pasarela de pago», «marketplace», «transportadora»); no recomiendan ni describen a ningún proveedor real.

Aplica cada comprobación con la matriz de caso no declarado de [metodo.md](metodo.md) §3 (declared / neighbor / boundary / failure). Un caso sin evidencia es «no comprobado».

| Código | Comprobación | Fallo típico que busca | Evidencia esperada |
|---|---|---|---|
| **C1** | **Permanente vs transitorio.** ¿Distingue errores permanentes (rechazo, datos inválidos) de transitorios (tiempo agotado, 5xx, límite de tasa)? | Reintentar un rechazo definitivo o abandonar ante un fallo transitorio | Clasificación explícita de códigos/estados y política de reintento con tope y espera creciente |
| **C2** | **Intento vs resultado final.** ¿Separa «se envió la solicitud» de «el proveedor confirmó el resultado final»? | Marcar como pagado/enviado/publicado algo solo intentado | Estado intermedio (p. ej. `pendiente`) y transición solo con confirmación del resultado final |
| **C3** | **Pendientes con vencimiento.** ¿Todo estado pendiente tiene plazo y acción al vencer? | Pendientes eternos que nadie revisa | Vencimiento declarado, tarea de conciliación y alerta al vencer |
| **C4** | **Notificación no verificada.** ¿Una notificación entrante (webhook, callback, correo) solo dispara una **consulta autenticada** al proveedor, en vez de cambiar el estado por sí misma? | Aceptar una notificación falsificada o repetida como verdad | Verificación de firma cuando exista **y** consulta autenticada del estado antes de actuar; idempotencia ante repeticiones |
| **C5** | **Importe nunca inferido.** ¿El importe, la moneda y la cantidad salen de una fuente autoritativa, nunca de la notificación, del cliente o de un cálculo implícito? | Cobrar o reembolsar un importe manipulado o mal redondeado | Importe leído del registro propio o de la consulta autenticada; comparación exacta antes de confirmar |
| **C6** | **Lo común en la capa común.** ¿Reintentos, idempotencia, firma, conciliación y registro viven en una capa compartida y no se reimplementan por proveedor? | Cada integración con su propio bug de reintento | Un módulo común usado por todos los adaptadores; los adaptadores solo traducen |
| **C7** | **Más allá del caso declarado.** ¿Se prueba algo más que el caso feliz que el autor declaró? | «Funciona» solo para el ejemplo de la demo | Pruebas de vecino, límite y fallo (duplicado, parcial, fuera de orden, vencido) además del caso declarado |

Cómo reportarlo: cita el código (C1…C7) en la objeción, con la localización exacta y el caso de la matriz que falta. Si el artefacto **solo** declara el caso feliz de una integración, es un hallazgo C7 de severidad al menos `major`, y `blocker` si hay dinero o envíos reales.

Ejemplos neutros:

- Una pasarela de pago confirma por webhook: si el código marca el pedido como pagado al recibir el webhook, sin consultar el estado autenticado ni comparar el importe, aplican C4 y C5.
- Una transportadora devuelve `timeout` al crear la guía: si se reintenta sin clave de idempotencia, puede duplicarse el envío (C1, C6).
- Un marketplace deja una publicación «en revisión»: sin vencimiento ni conciliación queda pendiente para siempre (C3), y mostrarla como publicada viola C2.
