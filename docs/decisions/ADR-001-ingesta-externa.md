# ADR-001: Ingesta externa desacoplada con GitHub Actions hacia Unity Catalog Volume

- **Estado:** Aceptado
- **Fecha:** 2026-11-05
- **Ticket relacionado:** SKY-001 / SKY-006 / SKY-010

## Contexto

El proyecto **SkyLake** captura snapshots de estados de aeronaves desde la API pública de **OpenSky Network** (`/api/states/all`) y los procesa en **Databricks Free Edition**.

Databricks Free Edition presenta dos restricciones clave para la captura de datos externos:
1. **Salida a internet restringida:** El entorno serverless limita las conexiones salientes a dominios de confianza, por lo que las llamadas directas a `opensky-network.org` pueden ser bloqueadas.
2. **Cuota de compute serverless limitada:** Despertar un cluster/warehouse o ejecutar un notebook en Databricks cada 30 minutos únicamente para realizar una petición HTTP y guardar un archivo JSON consume cuota de compute de forma innecesaria, con el riesgo de apagar el compute hasta el reinicio del límite.

## Decisión

Incluso si OpenSky resultara accesible desde el compute de Databricks, **mantenemos la ingesta fuera de Databricks** mediante un workflow programado en **GitHub Actions** (`cron: '*/30 * * * *'`):
1. Un runner ligero de GitHub Actions ejecuta `src/ingestion/opensky_to_volume.py`.
2. El script se autentica contra OpenSky (OAuth2 `client_credentials`), consulta el bounding box de América Latina con política de reintentos y backoff exponencial (`urllib3.util.retry.Retry`), y obtiene el snapshot JSON.
3. Mediante el **Databricks SDK para Python** (`WorkspaceClient().files.upload`), sube el archivo crudo directamente al Volume de Unity Catalog `/Volumes/skylake/bronze/landing/opensky/states/states_{ts}.json` usando un nombre determinista basado en el timestamp `time` del payload para garantizar idempotencia.
4. En Databricks, el pipeline declarativo (`skylake_pipeline`) consume incrementalmente los archivos nuevos mediante **Auto Loader** (`read_files`) en frecuencia más espaciada (ej. cada 60 minutos).

## Alternativas descartadas

1. **Notebook de ingesta ejecutado por un Databricks Job cada 30 minutos:**
   - *Motivo de descarte:* Bloqueo potencial de red saliente en Free Edition y consumo excesivo de la cuota diaria de compute serverless en esperas de I/O de red.
2. **Almacenamiento intermedio en un bucket S3/GCS/ADLS propio:**
   - *Motivo de descarte:* Requiere configurar credenciales de nube externas y External Locations de Unity Catalog, las cuales están restringidas o añaden fricción innecesaria frente al almacenamiento gestionado de un Unity Catalog Volume (`w.files.upload`).

## Consecuencias

- **Positivas:**
  - Cero consumo de cuota de compute de Databricks durante la captura de snapshots.
  - Desacoplamiento limpio entre adquisición de datos y procesamiento analítico (patrón estándar en producción).
  - Idempotencia garantizada en la capa de aterrizaje gracias al nombrado determinista `states_{ts}.json` con `overwrite=True`.
- **Negativas / Trade-offs:**
  - Los cron de GitHub Actions pueden sufrir retrasos de algunos minutos en horas de alta demanda y se desactivan tras largos periodos de inactividad en repositorios públicos, lo cual es tolerable porque la capa Bronze es incremental (`Auto Loader`) y las métricas horarias toleran huecos.
