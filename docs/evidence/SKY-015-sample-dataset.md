# Evidencia: SKY-015 (Dataset de muestra — Plan B)

- **Fecha:** 2026-11-25
- **Ticket:** `SKY-015` (#13)
- **Rama:** `feat/SKY-015-sample-dataset`
- **Estado:** Completado

---

## 1. Contenido del dataset de muestra (`data/sample/`)

Para garantizar que un tercero pueda reproducir de punta a punta **Bronze, Silver (incluyendo SCD Tipo 2) y Gold** sin depender de la API de OpenSky Network ni consumir cuota externa, se versionó en `data/sample/`:

1. **20 snapshots reales de OpenSky (`data/sample/states_*.json`):**
   - Descargados directamente desde `/Volumes/skylake/bronze/landing/opensky/states/`.
   - Rango de épocas: `states_1795142544.json` a `states_1795660294.json` (~3.83 MB en total, 14,927 aeronaves únicas observadas sobre América Latina).
2. **2 snapshots compactos de aeronaves (`data/sample/reference/aircraft/aircraft_2026_11.csv` y `aircraft_2026_12.csv`):**
   - Filtrados desde el catálogo oficial de OpenSky para conservar las **13,451** aeronaves observadas que cruzan con el catálogo más las **50** aeronaves con cambio en `operator_name` (`13,501` filas por CSV, ~671 KB cada uno).
   - Permite reproducir tanto el cruce dimensional como el historial real de cambios en `silver.dim_aircraft_scd2` sin subir los CSV completos de 28 MB a Git.

---

## 2. Script `scripts/load_sample.py` y entorno `uv`

- Se implementó `scripts/load_sample.py` usando `WorkspaceClient().files.upload(..., overwrite=True)` del SDK de Databricks.
- Comportamiento idempotente por defecto: consulta los archivos existentes en el Volume y omite los ya cargados para no sobrescribir snapshots procesados ni reemplazar el catálogo completo de aeronaves si ya está presente (admite `--overwrite` y `--volume-root`).
- Se configuró `pyproject.toml` y `uv.lock` para ejecución reproducible con `uv sync` y validación con `uv run pytest` (`tests/test_load_sample.py`).

---

## 3. Verificación ejecutada

### 3.1 Pruebas unitarias y linter (`uv`)
```text
$ uv run ruff check scripts/load_sample.py tests/test_load_sample.py
All checks passed!

$ uv run pytest -v
tests/test_load_sample.py::test_load_sample_dataset_uploads_all_into_empty_volume PASSED [ 33%]
tests/test_load_sample.py::test_load_sample_dataset_skips_existing_unless_overwrite PASSED [ 66%]
tests/test_load_sample.py::test_load_sample_dataset_raises_when_missing_states PASSED [100%]
3 passed in 2.18s
```

### 3.2 Ejecución contra Volume en vivo (idempotencia) y destino limpio (`_test_sky015`)
```text
$ uv run python scripts/load_sample.py
Resumen Plan B -> states subidos: 0 (omitidos: 20), referencia subida: 0 (omitidos: 2)

$ uv run python scripts/load_sample.py --volume-root /Volumes/skylake/bronze/landing/_test_sky015
Resumen Plan B -> states subidos: 20 (omitidos: 0), referencia subida: 2 (omitidos: 0)
Verified uploaded states: 20 ref: 2
Cleanup _test_sky015 OK
```
