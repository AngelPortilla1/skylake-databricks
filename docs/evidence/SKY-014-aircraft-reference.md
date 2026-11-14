# Evidencia: SKY-014 (Tabla de referencia de aeronaves)

- **Fecha:** 2026-11-13
- **Ticket:** `SKY-014` (#12)
- **Rama:** `feat/SKY-014-aircraft-reference`
- **Estado:** Completado

---

## 1. Origen y preparación de los snapshots

- **Fuente oficial:** OpenSky Network Aircraft Database (`https://s3.opensky-network.org/data-samples/metadata/aircraft-database-complete-2025-08.csv`).
- **Normalización:** Se extrajeron las 6 columnas útiles (`icao24`, `registration`, `manufacturer_name`, `model`, `operator_name`, `country`) en CSV estándar UTF-8 (616,648 registros válidos, 28.02 MB).
- **Preparación para SCD Tipo 2 (`SKY-023`):**
  - `aircraft_2026_11.csv`: snapshot base (616,648 filas).
  - `aircraft_2026_12.csv`: segunda versión con 50 aeronaves modificadas en `operator_name` (`... (Updated)`).
- **Ruta en Volume:** `/Volumes/skylake/bronze/landing/reference/aircraft/`.

---

## 2. Definición en `src/pipelines/01_bronze.sql`

Se agregó la streaming table `skylake.bronze.aircraft_db` leyendo incrementalmente desde `/Volumes/skylake/bronze/landing/reference/aircraft/` con Auto Loader (`format => 'csv'`, `header => true`).

---

## 3. Verificación en Databricks

- **Pipeline:** `skylake_pipeline` (`49ab89d2-2564-486b-a75b-e9306d08bac2`), update `a762e29a-c390-4c64-9be8-73206efcfa85` (`COMPLETED`).
- **Consulta de verificación en `Serverless Starter Warehouse`:**
  ```sql
  SELECT _source_file, count(*) AS rows_count
  FROM skylake.bronze.aircraft_db
  GROUP BY _source_file
  ORDER BY _source_file;
  ```
  Resultado:
  | `_source_file` | `rows_count` |
  |---|---|
  | `/Volumes/skylake/bronze/landing/reference/aircraft/aircraft_2026_11.csv` | `616648` |
  | `/Volumes/skylake/bronze/landing/reference/aircraft/aircraft_2026_12.csv` | `616648` |
