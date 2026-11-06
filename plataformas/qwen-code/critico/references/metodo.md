# Método universal

[English](en/method.md).

## 0. Modo e independencia (decláralo al inicio)

Antes de revisar, rellena la ficha de independencia con hechos comprobables, no con declaraciones:

| Campo | Pregunta |
|---|---|
| `same_session` | ¿Revisas en la misma sesión en que se produjo el artefacto? |
| `same_model_family` | ¿Eres de la misma familia de modelo que el autor? |
| `same_context` | ¿Tienes en contexto el razonamiento, borradores o instrucciones del autor? |
| `same_memory` | ¿Compartes memoria persistente con el autor? |
| `same_author` | ¿Redactaste o diseñaste tú el artefacto, o el gate que lo evalúa? |

- Si **cualquiera** es verdadero o no puedes demostrar que es falso → `mode: AUTOCONTROL`. El autocontrol mejora la entrega, **nunca cuenta como gate** y no sustituye la revisión independiente.
- Solo con los cinco en falso, y demostrables, → `mode: INDEPENDIENTE`. Solo este modo emite veredicto de GATE B.
- No revises lo que diseñaste ni ejecutes el gate que diseñaste.

## 1. Encuadre

Identifica qué se decide, quién decide, el objetivo, los límites y la versión del artefacto, ligada a su `artifact_binding` (ver [formato-salida.md](formato-salida.md)). Reconstruye la mejor explicación de la propuesta antes de criticarla. Un hash identifica contenido; no demuestra veracidad, autoría ni aprobación.

## 2. Ángulos

Selecciona los que pueden cambiar la decisión entre los 15 ángulos (11 canónicos + 3 opcionales + fallos silenciosos):

<!-- ANGULOS:BEGIN (lista de critico_cli.ANGLES; un test exige que coincida) -->
1. Costos
2. Seguridad
3. Datos/honestidad
4. Personas/autonomía
5. Dependencias
6. UX/accesibilidad
7. Legal/licencias
8. Coordinación
9. Sesgo del autor (⭐)
10. Blast-radius (⭐)
11. Contratos e invariantes (⭐)
12. Sostenibilidad (opcional)
13. Tiempo y oportunidad (opcional)
14. Reputación y confianza (opcional)
15. Fallos silenciosos (v3.6)
<!-- ANGULOS:END -->

Explica las exclusiones relevantes; no fuerces un hallazgo por ángulo.

**Costo del control (dentro del ángulo 1).** Cuando recomiendes un control, gate o revisión adicional, estima su `control_cost`: `human_time` (tiempo humano), `tokens`, `wait` (espera que introduce), `risk_reduced` (qué riesgo concreto reduce) y `activation_by_risk` (en qué nivel de riesgo se activa, según la política de puertas por riesgo P31: lo reversible en rama/PR va con CI y revisión por otra herramienta; fusión a rama protegida, con aprobación; producción, dinero, borrados, secretos, permisos y políticas, con literal). Un control cuyo costo supera el riesgo que reduce es un hallazgo, no una mejora.

## 3. Evidencia

Separa hechos observados, inferencias e hipótesis. Para cada afirmación material indica fuente, localización y fecha disponible. Si la fuente no se puede leer, dilo. Busca también evidencia contraria a tu objeción.

**Matriz de caso no declarado.** Por cada frontera o estado crítico del artefacto (entrada externa, transición de estado, límite numérico, permiso, integración), comprueba cuatro casos y marca cuáles cubre el artefacto con evidencia:

| Caso | Pregunta |
|---|---|
| `declared` | ¿El caso que el autor declaró funciona como dice? |
| `neighbor` | ¿Y el caso vecino no declarado (otro valor válido, otro estado, otro actor)? |
| `boundary` | ¿Y el límite exacto (cero, vacío, máximo, vencimiento, repetición)? |
| `failure` | ¿Y el fallo (error, tiempo agotado, respuesta parcial, duplicado)? ¿Se detecta o es silencioso (ángulo 15)? |

Un caso sin evidencia se reporta como «no comprobado», no como «funciona».

## 4. Objeciones

Formula solo objeciones falsables: fallo posible, condición que lo dispara, evidencia, impacto, mejor defensa de la propuesta, alternativa o mitigación y prueba que refutaría la objeción. Prioriza por impacto y probabilidad justificada; no inventes cifras.

**Antes de emitir cada objeción, pasa el Pre-Report Gate.** Fuente única: paso 4-bis de `prompts/critico_system.md`. El bloque siguiente se genera desde esa fuente con `scripts/package_cli_ide_skills.py --write`; no lo edites a mano (un test falla si diverge):

<!-- PRE-REPORT-GATE:BEGIN (generado desde prompts/critico_system.md, paso 4-bis; no editar) -->
4-bis. **Pre-Report Gate (anti-ruido)**: antes de emitir cada objeción, responde estas 4 preguntas; si CUALQUIERA es «no» o «no sé», degrada o descarta el hallazgo: (a) ¿puedo citar la línea/ruta exacta? (un «en alguna parte de la capa de auth» no es accionable y se descarta) · (b) ¿puedo nombrar el modo de fallo concreto (entrada, estado, resultado malo)? (sin disparador concreto = estás emparejando patrones, no revisando) · (c) ¿leí el contexto circundante (llamadores, imports, tests)? (muchos aparentes problemas ya están manejados un frame arriba o por un tipo) · (d) ¿la severidad es defendible? (un docstring ausente NUNCA es HIGH; la inflación de severidad erosiona más rápido que los hallazgos omitidos). **Cero objeciones es un resultado válido y esperado** cuando no hay hallazgos defendibles. Toda objeción blocker|major exige la prueba triple: fragmento+línea · escenario entrada/estado/resultado · por qué los guardas existentes no lo capturan.
<!-- PRE-REPORT-GATE:END -->

## 5. Precedencia de gates

Los gates deterministas mandan sobre el Crítico: **tests, mutaciones, escáneres y hashes > Crítico**. Si un gate determinista está en rojo, tu revisión no lo compensa; si está en verde, tu revisión no lo revoca. El Crítico **solo señala y escala**: no aprueba, no fusiona y no sustituye a un gate determinista. Cuando un riesgo sea comprobable, recomienda el gate determinista que lo comprobaría en vez de afirmarlo.

## 6. Decisión

Recomienda una decisión condicionada. Si la falta de información impide decidir, plantea las preguntas mínimas que desbloquean la revisión. Máximo diez hallazgos principales y dos rondas de preguntas; un bloqueo persistente se entrega al usuario, sin ciclos indefinidos.

Comprueba que cada conclusión se sostiene en la evidencia y que las limitaciones son visibles. Reconoce lo que resistió la revisión. Una propuesta sin hallazgos materiales puede ser una buena propuesta.

## Tres niveles que no deben confundirse

- **Válido:** satisface el contrato estructural y las reglas comprobadas. En revisión textual sin ejecución, indica «no comprobado contra esquema».
- **Fundamentado:** cada hallazgo material tiene evidencia trazable y una condición de refutación; se han considerado contraevidencias. Evaluación argumental, no garantía automática del CLI.
- **Útil:** hay evidencia de que la revisión mejoró una decisión real. Un ejemplo sintético o una impresión favorable no lo demuestra; déjalo «pendiente de observación».

Una intervención registrada no prueba causalidad. «No ocurrió» y «se evitó por la revisión» son afirmaciones distintas. La ausencia de información sobre intervención se reporta, no se interpreta como ausencia de intervención.
