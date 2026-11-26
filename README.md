# SkyLake: Observatorio de Tráfico Aéreo en Databricks Free Edition

Lakehouse de punta a punta construido sobre **Databricks Free Edition** con posiciones reales de aeronaves de **OpenSky Network** sobre América Latina.

## Objetivo y alcance

Este proyecto demuestra la implementación de un Lakehouse moderno adaptado a las restricciones reales de **Databricks Free Edition**:
- **Ingesta incremental desacoplada** con GitHub Actions hacia Unity Catalog Volumes (`skylake.bronze.landing`).
- **Arquitectura Medallion** (Bronze, Silver, Gold) en un único pipeline declarativo (**Lakeflow Spark Declarative Pipelines**) con Auto Loader (`read_files`).
- **Calidad de datos declarativa** con Expectations, tabla de cuarentena (`rejected_records`) y deduplicación con `AUTO CDC` (SCD Tipo 1).
- **Historial de dimensiones** de aeronaves con **SCD Tipo 2** (`AUTO CDC`).
- **Modelado dimensional y análisis geoespacial** en Gold usando vistas materializadas, indexación espacial **H3**, Liquid Clustering y detección heurística de anomalías ADS-B.
- **Orquestación y observabilidad** con Lakeflow Jobs, control de frescura y registro de métricas desde `event_log`.
- **Infraestructura como código y CI/CD** mediante Databricks Asset Bundles (DABs) y GitHub Actions.

> **Nota sobre detección de anomalías:** Las reglas implementadas en Gold (`skylake.gold.flight_anomalies`) son heurísticas basadas en conocimiento del dominio y no constituyen un sistema de seguridad operacional; los datos ADS-B contienen ruido y pueden presentar falsos positivos.

---

## Arquitectura

```text
GitHub Actions (cron, cada 30 min)
  │ llama a OpenSky con reintentos y sube el JSON crudo
  ▼
Volume skylake.bronze.landing (/opensky/states/*.json)
  ▼
┌────────── Un solo pipeline declarativo (límite de Free Edition) ──────────┐
│ Bronze: streaming tables con read_files (Auto Loader)                     │
│ Silver: limpieza, expectations, cuarentena, SCD1 (posiciones) y SCD2      │
│ Gold:   modelo dimensional (Materialized Views), H3, métricas, anomalías  │
└───────────────────────────────────────────────────────────────────────────┘
  ▼
Dashboard AI/BI + Genie Space · Job (cada 60 min) · alertas · ops.pipeline_runs
```

---

## Estructura del repositorio

```text
skylake-databricks/
├── databricks.yml                 # Configuración de Databricks Asset Bundle (DABs)
├── resources/                     # Definiciones de jobs y pipelines en YAML
├── src/
│   ├── ingestion/                 # Script de ingesta desde OpenSky hacia UC Volume
│   ├── pipelines/                 # SQL declarativo del pipeline (01_bronze, 02_silver, 03_gold)
│   └── utils/                     # Utilidades compartidas
├── scripts/                       # Scripts de soporte (carga de dataset de muestra, etc.)
├── data/sample/                   # Snapshots de ejemplo (Plan B reproducible sin API)
├── tests/
│   └── sql/                       # Checks de calidad en SQL (silver_checks.sql)
├── docs/
│   ├── decisions/                 # Architecture Decision Records (ADRs)
│   ├── evidence/                  # Capturas y resultados de validación por ticket
│   └── free-edition-findings.md   # Bitácora técnica de límites y adaptaciones en Free Edition
└── .github/workflows/             # Workflows de ingesta programada y CI/CD
```

---

## Reproducción rápida con dataset de muestra (Plan B)

El directorio `data/sample/` incluye **20 snapshots reales** capturados de OpenSky Network sobre América Latina (`states_*.json`, ~3.8 MB) y **2 snapshots compactos del catálogo de aeronaves** (`reference/aircraft/aircraft_2026_11.csv` y `aircraft_2026_12.csv`, con 13,501 aeronaves observadas y 50 cambios de operador para demostrar SCD Tipo 2). Esto permite reproducir **Bronze, Silver y Gold** de punta a punta sin depender de la API de OpenSky ni consumir créditos externos:

1. Crea en Databricks el catálogo, schemas y Volume ejecutando `scripts/00_setup_catalog.sql` en el SQL Editor (si es un workspace nuevo).
2. Configura tus variables de entorno copiando `.env.example` a `.env` con tu `DATABRICKS_HOST` y `DATABRICKS_TOKEN`.
3. Sincroniza el entorno con `uv` y sube la muestra al Volume `skylake.bronze.landing`:
   ```bash
   uv sync
   uv run python scripts/load_sample.py
   ```
   *(Alternativa sin `uv`: `pip install -r requirements-ingest.txt && python scripts/load_sample.py` exportando antes `DATABRICKS_HOST` y `DATABRICKS_TOKEN`).*
   - Por defecto, `load_sample.py` es idempotente: solo sube archivos ausentes en el Volume para no sobrescribir datos ya ingeridos. Usa `--overwrite` si deseas forzar la recarga.
4. Ejecuta el pipeline declarativo `skylake_pipeline` desde **Jobs & Pipelines** en Databricks para poblar todas las tablas de Bronze, Silver y Gold.

---

## Documentación adicional

- [Guía de contribución y convenciones (`CONTRIBUTING.md`)](CONTRIBUTING.md)
- [Bitácora de hallazgos en Free Edition (`docs/free-edition-findings.md`)](docs/free-edition-findings.md)
- [Decisiones de arquitectura (`docs/decisions/`)](docs/decisions/)
