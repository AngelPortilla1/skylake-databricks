# Guía de Contribución y Convenciones (SkyLake)

Este documento define las normas de nomenclatura, flujo de ramas, commits y Pull Requests para el proyecto **SkyLake**.

## 1. Convenciones de nombres

- **Estilo general:** `snake_case` para todos los identificadores SQL (catálogos, schemas, tablas, vistas, columnas), scripts de Python y archivos de configuración.
- **Catálogo y Schemas:**
  - Catálogo principal: `skylake`
  - Capas Medallion y operaciones: `skylake.bronze`, `skylake.silver`, `skylake.gold`, `skylake.ops`
  - Volume de aterrizaje: `skylake.bronze.landing`
- **Tablas en capa Gold:**
  - Tablas de hechos con prefijo `fact_` (ej. `fact_flight_positions`).
  - Tablas de dimensiones con prefijo `dim_` (ej. `dim_aircraft`, `dim_country`, `dim_time`).
- **Columnas técnicas y de metadatos:**
  - Deben iniciar con guion bajo (`_`), por ejemplo: `_ingested_at`, `_source_file`, `_source_modified_at`.
  - Las columnas generadas automáticamente por SCD Tipo 2 conservan el doble guion bajo de Lakeflow (`__START_AT`, `__END_AT`) en Silver y se exponen como `valid_from`, `valid_to` e `is_current` en Gold.

---

## 2. Flujo de ramas y commits

- **Rama principal:** `main` está protegida. Ningún cambio se sube directamente a `main` una vez configurada la protección.
- **Ramas por ticket:** Se crea una rama por cada ticket siguiendo el formato:
  ```text
  feat/SKY-XXX-descripcion-corta
  ```
  *Ejemplo:* `feat/SKY-021-dedup-silver`
- **Formato de commits:** Cada commit debe referenciar el código del ticket seguido de una descripción concisa en español:
  ```text
  SKY-XXX: descripción clara del cambio
  ```
  *Ejemplo:* `SKY-021: deduplicación por icao24 y time`
- **Pull Requests:** Se abre **un PR por ticket** hacia `main`.

---

## 3. Definición de Hecho (Definition of Done)

Un ticket se considera **Hecho** únicamente cuando cumple los tres requisitos:
1. **Criterio de aceptación cumplido** según el plan de trabajo.
2. **Evidencia guardada** en `docs/evidence/` (captura de pantalla o salida de consulta SQL/CLI en Markdown).
3. **Documentación actualizada** (`README.md`, ADRs en `docs/decisions/` si aplica, y cualquier restricción encontrada registrada en `docs/free-edition-findings.md`).

---

## 4. Plantilla de Pull Request

Todo PR utiliza automáticamente la plantilla ubicada en `.github/pull_request_template.md`, que incluye:
- **Ticket:** Referencia al issue (`Closes #N` / `SKY-XXX`).
- **¿Qué cambia?:** Resumen de los archivos y componentes creados o modificados.
- **¿Cómo se probó?:** Pasos y consultas ejecutadas para verificar el criterio de aceptación.
- **Enlace a la evidencia:** Ruta al archivo correspondiente dentro de `docs/evidence/`.
