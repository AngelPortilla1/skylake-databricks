# Evidencia: SKY-011 (Programación con GitHub Actions, reintentos y manejo de fallos)

- **Fecha:** 2026-11-25
- **Ticket:** `SKY-011` (#9)
- **Rama:** `feat/SKY-011-resilience-evidence`
- **Workflow:** `.github/workflows/ingest.yml` (`ingest-opensky`)
- **Estado:** Completado

---

## 1. Estabilidad en producción (> 24 horas)

El workflow programado (`cron: '*/30 * * * *'`) operó de manera autónoma desde el **2026-11-13** hasta el **2026-11-26** (~13 días continuos):

- **Total de ejecuciones registradas:** `47` (`44` por `schedule` y `3` por `workflow_dispatch`).
- **Ejecuciones exitosas:** `47 / 47` (**100 % de tasa de éxito**, superando el umbral de ≥ 90 % exigido por el criterio de aceptación).
- **Duración típica por corrida:** `15s – 27s` en `ubuntu-latest` (muy por debajo del `timeout-minutes: 5`).
- **Observación operativa:** En repositorios públicos, el planificador `schedule` de GitHub Actions aplica retrasos u omisiones en horas de alta demanda (promediando ~3–4 ejecuciones efectivas al día). Dado que Bronze usa Auto Loader incremental y Silver deduplica por `icao24 + position_ts`, los intervalos variables se absorben sin pérdida de integridad.

---

## 2. Pruebas de resiliencia

### 2.1 Concurrencia e idempotencia ante ejecuciones seguidas (`workflow_dispatch`)

Se dispararon dos ejecuciones manuales consecutivas con dos segundos de diferencia (`2026-11-26T04:34:26Z` y `2026-11-26T04:34:28Z`):

- **Run 1 (`45756069118`):** Ejecutó inmediatamente (`27s` total) y depositó:
  ```text
  OK /Volumes/skylake/bronze/landing/opensky/states/states_1795667683.json (769 estados)
  ```
- **Run 2 (`45756072534`):** Gracias a `concurrency: { group: ingest-opensky, cancel-in-progress: false }`, esperó en cola a que finalizara el Run 1 sin cancelarlo (`40s` total) y depositó:
  ```text
  OK /Volumes/skylake/bronze/landing/opensky/states/states_1795667692.json (767 estados)
  ```
- Cuando dos ejecuciones obtienen el mismo epoch `time` de OpenSky, la ruta determinista `states_{ts}.json` combinada con `w.files.upload(..., overwrite=True)` sobrescribe el archivo sin generar duplicados en el Volume.

### 2.2 Fallo de credenciales (`exit code 1`)

Ejecución de `src/ingestion/opensky_to_volume.py` con un token inválido (`DATABRICKS_TOKEN=dapi_invalid_token_test`):

```text
Unexpected status resolving file endpoints (403, request ID 4d2f6438-adb2-442f-8bbd-0fbabc5a7f84), using the default endpoints.
ERROR: PermissionDenied: Invalid access token. [ReqId: 8de63166-834e-4b33-af34-c2b4404d8c32].
Cred fail exit code: 1
```

El script captura la excepción, escribe el diagnóstico en `stderr` sin exponer el valor del secreto (`token=***`) y finaliza con código de salida `1`, marcando el job de GitHub Actions en rojo y activando la notificación por correo de fallo.

### 2.3 Fallo de red y reintentos exponenciales (`Retry`)

Simulación apuntando `API_URL` a un endpoint inalcanzable (`https://127.0.0.1:9/api/states/all`) con el adaptador `HTTPAdapter(max_retries=Retry(...))`:

```text
DEBUG:urllib3.connectionpool:Starting new HTTPS connection (1): 127.0.0.1:9
WARNING:urllib3.connectionpool:Retrying (Retry(total=2, ...)) after connection broken by 'NewConnectionError(...)'
DEBUG:urllib3.connectionpool:Starting new HTTPS connection (2): 127.0.0.1:9
WARNING:urllib3.connectionpool:Retrying (Retry(total=1, ...)) after connection broken by 'NewConnectionError(...)'
DEBUG:urllib3.connectionpool:Starting new HTTPS connection (3): 127.0.0.1:9
WARNING:urllib3.connectionpool:Retrying (Retry(total=0, ...)) after connection broken by 'NewConnectionError(...)'
DEBUG:urllib3.connectionpool:Starting new HTTPS connection (4): 127.0.0.1:9
ERROR: ConnectionError: HTTPSConnectionPool(host='127.0.0.1', port=9): Max retries exceeded with url: /api/states/all...
Net retry exit code: 1
```

En producción (`total=5, backoff_factor=2, status_forcelist=[429, 500, 502, 503, 504], respect_retry_after_header=True`), el cliente absorbe caídas transitorias y límites `429` antes de fallar limpiamente con `exit 1`.
