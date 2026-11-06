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

Para reproducir Bronze, Silver y Gold sin depender de la API de OpenSky ni agotar cuota:

1. Configura tus variables de entorno copiando `.env.example` a `.env` con tu `DATABRICKS_HOST` y `DATABRICKS_TOKEN`.
2. Instala las dependencias de ingesta:
   ```bash
   pip install -r requirements-ingest.txt
   ```
3. Ejecuta el script de carga de muestra (disponible a partir de `SKY-015`):
   ```bash
   python scripts/load_sample.py
   ```
4. Ejecuta el pipeline `skylake_pipeline` desde Databricks.

---

## Documentación adicional

- [Guía de contribución y convenciones (`CONTRIBUTING.md`)](CONTRIBUTING.md)
- [Bitácora de hallazgos en Free Edition (`docs/free-edition-findings.md`)](docs/free-edition-findings.md)
- [Decisiones de arquitectura (`docs/decisions/`)](docs/decisions/)
