# Bitácora de Hallazgos en Databricks Free Edition

Registro técnico de pruebas, límites encontrados en **Databricks Free Edition**, su impacto en la arquitectura de **SkyLake** y las decisiones tomadas para resolverlos.

## Matriz de validación inicial (SKY-006)

| Fecha | Prueba | Resultado | Impacto | Decisión |
|---|---|---|---|---|
| Pendiente | **T1:** Salida a internet desde notebook (`opensky-network.org`, `github.com`, `pypi.org`) | Pendiente | Determina si Databricks puede consultar OpenSky directamente | Usar ingesta externa con GitHub Actions hacia el Volume (`ADR-001`) |
| Pendiente | **T2:** Subir archivo al Volume desde fuera (`databricks fs cp` / SDK) | Pendiente | Requerido para que GitHub Actions deposite los snapshots JSON en `skylake.bronze.landing` | Pendiente de validar en `SKY-006` |
| Pendiente | **T3:** Personal Access Token (PAT) en `Settings -> Developer -> Access tokens` | Pendiente | Requerido para autenticación automatizada desde GitHub Actions | Pendiente de validar en `SKY-006` |
| Pendiente | **T4:** Databricks Asset Bundle (`bundle validate`, `bundle deploy -t dev`) | Pendiente | Determina el alcance del despliegue continuo en la Etapa 6 | Pendiente de validar en `SKY-006` |
| Pendiente | **T5:** Pipeline declarativo serverless con tabla simple | Pendiente | Valida sintaxis `CREATE OR REFRESH STREAMING TABLE` y modo `availableNow` | Unificar Bronze, Silver y Gold en un único pipeline `skylake_pipeline` |
| Pendiente | **T6:** Grupos y permisos (`GRANT` en Unity Catalog) | Pendiente | Determina cómo implementar gobernanza en la Etapa 5 | Pendiente de validar en `SKY-006` |
| Pendiente | **T7:** Job con programación (`schedule`) y alerta por correo en caso de fallo | Pendiente | Requerido para orquestación y observabilidad en la Etapa 4 | Pendiente de validar en `SKY-006` |

---

## Registro cronológico de hallazgos adicionales

- **2026-11-05 (`SKY-003` — Integración de GitHub en Databricks Free Edition):** Al intentar hacer `Commit & Push` desde un Git folder en Databricks usando una cuenta vinculada de GitHub, el push falla con *"El enlace a tu cuenta de GitHub no tiene acceso"* hasta que se instala y autoriza explícitamente la **Databricks GitHub App** sobre el repositorio `skylake-databricks` (o se selecciona explícitamente el Fine-grained PAT con permiso `Contents: Read and write` en la pestaña *Settings* del Git folder).
- **2026-11-05 (`SKY-004` — Creación de catálogo propio `skylake` en Unity Catalog):** `CREATE CATALOG IF NOT EXISTS skylake` ejecutado en el `Serverless Starter Warehouse` (2X-Small) funcionó directamente usando el almacenamiento gestionado por defecto del metastore en Free Edition, sin necesidad de recurrir al catálogo `workspace` por defecto.



