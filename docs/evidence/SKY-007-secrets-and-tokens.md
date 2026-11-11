# Evidencia: SKY-007 (Secretos y tokens)

- **Fecha:** 2026-11-10
- **Ticket:** `SKY-007` (#7)
- **Estado:** Completado

---

## 1. Generación de Personal Access Token (PAT) en Databricks para CI/CD
Se creó el token dedicado para automatización e ingesta desde GitHub Actions mediante `databricks tokens create --comment "skylake-github-actions-ci" --profile skylake-dev`:
- `token_id`: `16672f0ca29b6d03611a35eab730c79119e93cc562349870d2a53e21f37c4542`
- `comment`: `skylake-github-actions-ci`

---

## 2. Secretos configurados en GitHub Actions (`gh secret list`)
Se cargaron los 4 secretos requeridos en el repositorio `AngelPortilla1/skylake-databricks` (`Settings -> Secrets and variables -> Actions`):

```text
NAME                   UPDATED
DATABRICKS_HOST        2026-11-06T03:37:02Z
DATABRICKS_TOKEN       2026-11-11T04:27:08Z
OPENSKY_CLIENT_ID      2026-11-11T04:33:20Z
OPENSKY_CLIENT_SECRET  2026-11-11T04:33:23Z
```

---

## 3. Verificación de `.env.example`, `.gitignore` e historial de Git
- Plantilla versionada en `.env.example` sin valores sensibles:
  ```ini
  # Variables de entorno para SkyLake (copiar a .env y completar valores reales)
  DATABRICKS_HOST=https://dbc-xxxxxxxx-xxxx.cloud.databricks.com
  DATABRICKS_TOKEN=
  OPENSKY_CLIENT_ID=
  OPENSKY_CLIENT_SECRET=
  ```
- Estado de `.env` local (ignorado por Git en `.gitignore` junto con `credentials.json`):
  ```text
  DATABRICKS_HOST=<SET>
  DATABRICKS_TOKEN=<SET>
  OPENSKY_CLIENT_ID=<SET>
  OPENSKY_CLIENT_SECRET=<SET>
  ```
- Verificación de ausencia de secretos en el historial del repositorio (`git log --all --full-history -- ".env" "credentials.json"`): **0 commits**.
