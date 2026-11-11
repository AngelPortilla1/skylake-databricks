# Evidencia: SKY-006 (Validación de Databricks Free Edition)

- **Fecha:** 2026-11-10
- **Ticket:** `SKY-006` (#6)
- **Estado:** Completado
- **Entorno CLI:** `Databricks CLI v1.25.0` autenticado con OAuth U2M (`--profile skylake-dev`)

---

## Resumen de las 7 pruebas ejecutadas

### T1: Salida a internet desde compute serverless
- **Ejecución:** Job serverless (`run_id: 819661157589396`, `task_run_id: 970156400426196`) ejecutando peticiones HTTP `GET` con `requests` (`timeout=10`).
- **Resultado:**
  ```json
  {
    "https://opensky-network.org/api/states/all?lamin=4&lomin=-75&lamax=5&lomax=-73": "OK (200)",
    "https://github.com": "OK (200)",
    "https://pypi.org": "OK (200)"
  }
  ```
- **Decisión:** Aunque `opensky-network.org` responde `200 OK`, se mantiene la ingesta externa con GitHub Actions documentada en `ADR-001` para no consumir cuota de compute serverless en capturas cada 30 minutos.

---

### T2: Subir archivo al Volume desde fuera (`databricks fs cp`)
- **Ejecución:**
  ```powershell
  databricks fs mkdirs dbfs:/Volumes/skylake/bronze/landing/test --profile skylake-dev
  databricks fs cp test.json dbfs:/Volumes/skylake/bronze/landing/test/test.json --overwrite --profile skylake-dev
  databricks fs ls dbfs:/Volumes/skylake/bronze/landing/test --profile skylake-dev
  databricks fs cat dbfs:/Volumes/skylake/bronze/landing/test/test.json --profile skylake-dev
  ```
- **Salida:**
  ```text
  C:\Users\Angel\AppData\Local\Temp\test.json -> dbfs:/Volumes/skylake/bronze/landing/test/test.json
  test.json
  {"test": "sky-006-t2", "status": "ok"}
  ```
- **Hallazgo:** `databricks fs cp` exige que el directorio destino exista previamente (`databricks fs mkdirs`), mientras que `WorkspaceClient().files.upload()` del SDK de Python crea los directorios intermedios automáticamente.

---

### T3: Personal Access Token (PAT)
- **Ejecución:**
  ```powershell
  databricks tokens create --comment "sky-006-t3-validation" --lifetime-seconds 3600 -o json --profile skylake-dev
  ```
- **Salida:**
  ```text
  T3 SUCCESS: token_id=fc52ef6ce9d8491d32d0819670373c85964126b79e5435d64676c82febe4684e, comment=sky-006-t3-validation, expiry=1794374471804
  ```
- **Decisión:** Free Edition permite generar PATs, lo que habilita la ingesta programada y el CI/CD desde GitHub Actions usando `DATABRICKS_TOKEN`.

---

### T4: Databricks Asset Bundle (`bundle validate` y `bundle deploy -t dev`)
- **Ejecución:**
  ```powershell
  databricks bundle validate --profile skylake-dev
  databricks bundle deploy -t dev --profile skylake-dev
  ```
- **Salida:**
  ```text
  Name: skylake
  Target: dev
  Workspace:
    User: angelportihernan019@gmail.com
    Path: /Workspace/Users/angelportihernan019@gmail.com/.bundle/skylake/dev

  Validation OK!
  Uploading bundle files to /Workspace/Users/angelportihernan019@gmail.com/.bundle/skylake/dev/files...
  Files: 27 uploaded, 0 deleted
  Resources: 0 created, 0 changed, 0 deleted, 0 unchanged
  ```

---

### T5: Pipeline declarativo serverless con tabla simple
- **Ejecución:** Se creó el pipeline temporal `sky_006_t5_validation` (`pipeline_id: 36e93a16-cc50-4dd0-a9f4-2401e9a798eb`, `serverless: true`, `continuous: false`, `edition: ADVANCED`) con la definición:
  ```sql
  CREATE OR REFRESH STREAMING TABLE skylake.ops._t5_validation_test
  COMMENT 'Tabla temporal de validacion SKY-006 T5'
  AS SELECT
    *,
    current_timestamp() AS _ingested_at,
    _metadata.file_path AS _source_file
  FROM STREAM read_files(
    '/Volumes/skylake/bronze/landing/test/',
    format => 'json'
  );
  ```
- **Actualización (`update_id: dc367fda-4237-4a2c-8b00-00522479026b`):** Finalizó en estado `COMPLETED`.
- **Consulta de verificación (`SELECT * FROM skylake.ops._t5_validation_test`):**
  ```json
  [
    {
      "_ingested_at": "2026-11-11T04:23:52.206Z",
      "_rescued_data": "",
      "_source_file": "/Volumes/skylake/bronze/landing/test/test.json",
      "status": "ok",
      "test": "sky-006-t2"
    }
  ]
  ```
  *(El pipeline y la tabla temporal fueron eliminados tras la prueba para mantener limpio el workspace).*

---

### T6: Grupos y permisos (`GRANT` en Unity Catalog)
- **Prueba 1 (Grupo local del workspace con `databricks groups create`):**
  - El grupo se crea en `/api/2.0/preview/scim/v2/Groups`, pero al ejecutar `GRANT USE CATALOG ON CATALOG skylake TO skylake_analysts_test` falla con:
    `ErrorClass=PRINCIPAL_DOES_NOT_EXIST: Could not find principal with name skylake_analysts_test.`
- **Prueba 2 (Grupo a nivel de cuenta con `/api/2.0/account/scim/v2/Groups` y `account users`):**
  - Se creó el grupo de cuenta `skylake_analysts_test` (`id: 85853628986554`) mediante `databricks api post /api/2.0/account/scim/v2/Groups` y se ejecutó `GRANT USE CATALOG ON CATALOG skylake TO skylake_analysts_test` y `SHOW GRANTS ON CATALOG skylake`:
    ```json
    [
      {
        "ActionType": "USE CATALOG",
        "ObjectKey": "skylake",
        "ObjectType": "CATALOG",
        "Principal": "skylake_analysts_test"
      }
    ]
    ```
  - Posteriormente se revocó el permiso y se eliminó el grupo de prueba.

---

### T7: Job con programación (`schedule`) y alerta por correo (`email_notifications`)
- **Ejecución:** Creación de Job serverless (`job_id: 1006731101676165`) con cron Quartz y notificación de fallo por correo:
  ```json
  {
    "schedule": {
      "pause_status": "PAUSED",
      "quartz_cron_expression": "0 0 * * * ?",
      "timezone_id": "UTC"
    },
    "email_notifications": {
      "on_failure": ["angelportihernan019@gmail.com"]
    }
  }
  ```
- **Resultado:** Verificado exitosamente con `databricks jobs get 1006731101676165` y limpiado tras la prueba.

