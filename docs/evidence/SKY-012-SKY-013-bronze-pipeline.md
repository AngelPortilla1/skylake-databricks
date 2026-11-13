# Evidencia: SKY-012 y SKY-013 (Pipeline Bronze con Auto Loader y metadatos)

- **Fecha:** 2026-11-12
- **Tickets:** `SKY-012` (#10) y `SKY-013` (#11)
- **Rama:** `feat/SKY-012-bronze-pipeline`
- **Estado:** Completado

---

## 1. Pipeline creado

- **Nombre:** `skylake_pipeline`
- **Pipeline ID:** `49ab89d2-2564-486b-a75b-e9306d08bac2`
- **Configuración:** `serverless: true`, `continuous: false` (modo incremental `availableNow`), `edition: ADVANCED`, `catalog: skylake`, `schema: bronze`.
- **Fuente:** `/Workspace/Users/angelportihernan019@gmail.com/skylake-databricks/src/pipelines/**` (`src/pipelines/01_bronze.sql`).
- **Update exitoso:** `5b2453d2-7f7c-4680-84f1-5990a756001d` (`COMPLETED`).

> **Nota técnica:** Al incluir `src/pipelines/**`, Lakeflow rechazó `.gitkeep` con `[UNSUPPORTED_LIBRARY_FILE_TYPE]` (solo admite `.sql` o `.py`), por lo que se eliminó `src/pipelines/.gitkeep`.

---

## 2. Verificación de datos en `skylake.bronze.flight_states_raw` (`SKY-012`)

Consulta ejecutada en `Serverless Starter Warehouse` (`63341ef5085658f5`):

```sql
SELECT time, size(states) AS n_states, _source_file, _source_modified_at, _ingested_at
FROM skylake.bronze.flight_states_raw
ORDER BY time DESC
LIMIT 10;
```

Resultado:

| time | n_states | _source_file | _source_modified_at | _ingested_at |
|---|---|---|---|---|
| `1794541973` | `1036` | `/Volumes/skylake/bronze/landing/opensky/states/states_1794541973.json` | `2026-11-13T03:52:58.000Z` | `2026-11-13T04:02:27.173Z` |
| `1794541569` | `1088` | `/Volumes/skylake/bronze/landing/opensky/states/states_1794541569.json` | `2026-11-13T03:46:15.000Z` | `2026-11-13T04:02:27.173Z` |
| `1794541550` | `1091` | `/Volumes/skylake/bronze/landing/opensky/states/states_1794541550.json` | `2026-11-13T03:46:00.000Z` | `2026-11-13T04:02:27.173Z` |

---

## 3. Validación de metadatos y `COMMENT` (`SKY-013`)

`DESCRIBE EXTENDED skylake.bronze.flight_states_raw` confirma:
- Columnas de metadatos presentes y pobladas: `_ingested_at` (`timestamp`), `_source_file` (`string`), `_source_modified_at` (`timestamp`).
- `Type`: `STREAMING_TABLE`
- `Comment`: `Snapshots crudos de OpenSky (states/all). Un registro por archivo.`
- `Last Refresh Type`: `INCREMENTAL`, `Latest Refresh Status`: `Succeeded`.
