# Política Kuvexta (solo cuando corresponda)

[English](en/kuvexta.md).

Esta referencia describe el reparto de funciones del proyecto; no autoriza acceso al workspace ni sustituye las reglas del repositorio dueño.

- Criba contrasta hechos; Crítico ataca supuestos; GATE C decide. Si trabajaste en el artefacto, declara la falta de independencia y solicita revisión externa cuando sea necesaria.
- Estados terminales: PASA, PASA_CON_CONDICIONES, NO_PASA, RIESGO_NO_EVALUADO. Suspensiones: NECESITA_INFO y REVISION_PARCIAL, con control de ciclo. No confundir una suspensión con aprobación o rechazo terminal.
- Un skip activo impide PASA: I3 exige NO_PASA y GATE_SKIPPED.
- M3 requiere preguntas resueltas, suspensión identificada y cambio del hash real frente al registrado al suspender. La forma de un veredicto, por sí sola, no prueba M3.
- Las propuestas de cambio y sus hashes no son actas de aprobación. No atribuyas palabras al decisor. Respeta el protocolo vigente de autorización fuera de esta skill.

La incorporación al workspace corresponde al encargado. Registro BZ, anclaje P01, check_encargo y P22 son comprobaciones del entorno de destino, que el encargado debe consultar y ejecutar allí. Este paquete no asegura conocer su estado ni las realiza.
