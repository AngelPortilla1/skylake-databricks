# Evidencia: SKY-010 (Script de ingesta OpenSky hacia el Volume)

- **Fecha:** 2026-11-12
- **Ticket:** `SKY-010` (#8)
- **Rama:** `feat/SKY-010-opensky-ingest`
- **Estado:** Completado

---

## 1. Implementación

- Script creado: `src/ingestion/opensky_to_volume.py`
  - Autenticación OAuth2 (`client_credentials`) contra OpenSky Network usando `OPENSKY_CLIENT_ID` y `OPENSKY_CLIENT_SECRET`.
  - Sesión HTTP con reintentos exponenciales (`Retry(total=5, backoff_factor=2, status_forcelist=[429, 500, 502, 503, 504])`).
  - Bounding box acotado para América Latina: `lamin=-56.0`, `lomin=-120.0`, `lamax=33.0`, `lomax=-30.0`.
  - Subida idempotente al Volume `/Volumes/skylake/bronze/landing/opensky/states/states_{ts}.json` mediante `WorkspaceClient().files.upload(..., overwrite=True)`.
- Dependencias declaradas en `requirements-ingest.txt`: `requests`, `databricks-sdk`.

---

## 2. Prueba local y verificación en el Volume

Ejecución local de `python src/ingestion/opensky_to_volume.py` en dos instantes distintos:

```text
OK /Volumes/skylake/bronze/landing/opensky/states/states_1794541550.json (1091 estados)
OK /Volumes/skylake/bronze/landing/opensky/states/states_1794541569.json (1088 estados)
```

Listado del directorio `/Volumes/skylake/bronze/landing/opensky/states` vía `WorkspaceClient().files.list_directory_contents`:

```text
[
  ('/Volumes/skylake/bronze/landing/opensky/states/states_1794541550.json', 146751),
  ('/Volumes/skylake/bronze/landing/opensky/states/states_1794541569.json', 146338)
]
```

*(Nota: el SDK emite el aviso informativo `Unexpected status resolving file endpoints (403, ...), using the default endpoints.` en Free Edition antes de completar la subida con éxito).*
