# Política Kuvexta (solo cuando corresponda)

[English](en/kuvexta.md).

Esta referencia describe el reparto de funciones del proyecto; no autoriza acceso al workspace ni sustituye las reglas del repositorio dueño.

- Criba contrasta hechos; Crítico ataca supuestos; GATE C decide. Si trabajaste en el artefacto, declara la falta de independencia y solicita revisión externa cuando sea necesaria.
- Estados terminales: PASA, PASA_CON_CONDICIONES, NO_PASA, RIESGO_NO_EVALUADO. Suspensiones: NECESITA_INFO y REVISION_PARCIAL, con control de ciclo. No confundir una suspensión con aprobación o rechazo terminal.
- Un skip activo impide PASA: I3 exige NO_PASA y GATE_SKIPPED.
- M3 requiere preguntas resueltas, suspensión identificada y cambio del hash real frente al registrado al suspender. La forma de un veredicto, por sí sola, no prueba M3.
- Las propuestas de cambio y sus hashes no son actas de aprobación. No atribuyas palabras al decisor. Respeta el protocolo vigente de autorización fuera de esta skill.

## Puertas por riesgo (P31)

El nivel de control lo fija el riesgo: trabajo reversible en rama, piloto o PR = libre con CI y revisión por otra herramienta; fusión a rama protegida = aprobación de Dirección en el PR; producción, dinero, borrados, secretos, permisos y políticas = literal de Dirección. Mientras el Crítico esté en piloto, su GATE B es consultivo en fronteras. Los gates deterministas (tests, mutaciones, escáneres, hashes) mandan sobre el Crítico; el Crítico señala y escala.

## El Crítico en dos niveles

| Nivel | Quién | Cuenta como gate | Salida |
|---|---|---|---|
| **AUTOCONTROL** | El propio autor, en su sesión, con la skill | **No** | Mejora la entrega antes de pedir revisión |
| **INDEPENDIENTE** | Revisor de otra familia de modelo, sin la sesión, el contexto ni la memoria del autor, y sin leer su autocontrol | Sí (GATE B) | Veredicto ligado al `artifact_binding` exacto |

**Separación:** nadie revisa lo que diseñó ni ejecuta el gate que diseñó. La independencia se demuestra con la ficha de [metodo.md](metodo.md) §0, no se declara.

**Expediente formal:** el registro de un GATE B (YAML de triage/objeciones/veredicto contra los esquemas y su entrada en la bitácora) es una **tarea aparte**, con su propio encargo; esta skill, en solo lectura, no lo crea ni afirma que exista.

## Protocolo de AUTOCONTROL

1. Etiqueta la salida «Crítico en sesión — <fecha> — AUTOCONTROL, no es gate».
2. Liga la salida al hash del head revisado y al sha256 de la skill usada (`SKILL.md` o el manifest de la skill).
3. No uses el autocontrol como evidencia de aprobación ni lo cites como GATE B.
4. Si el autocontrol encuentra un **blocker**, el autor **no declara «LISTO PARA REVISIÓN»** hasta corregirlo (o hasta dejarlo documentado como bloqueo para Dirección).

La incorporación al workspace corresponde al encargado. Registro BZ, anclaje P01, check_encargo y P22 son comprobaciones del entorno de destino, que el encargado debe consultar y ejecutar allí. Este paquete no asegura conocer su estado ni las realiza.
