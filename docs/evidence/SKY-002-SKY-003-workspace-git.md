# Evidencia: SKY-002 y SKY-003 (Workspace Free Edition y Git Folder Conectado)

- **Fecha:** 2026-11-05
- **Workspace URL (`DATABRICKS_HOST`):** `https://dbc-b6e41914-792d.cloud.databricks.com`
- **Tickets cubiertos:**
  - `SKY-002`: Workspace Free Edition verificado y accesible.
  - `SKY-003`: Git folder conectado en Databricks con el repositorio `AngelPortilla1/skylake-databricks` y commit realizado desde la interfaz de Databricks visible en GitHub.

## Verificación de Commit desde Databricks (`SKY-003`)

```text
commit d7143a75723f9fafd3f583da6a06ce4ff1e1bc68
Author: AngelPortilla1 <angelportihernan019@gmail.com>
Date:   Fri Nov 6 03:53:31 2026 +0000

    SKY-003: verificar commit desde Databricks Git folder

 src/ingestion/Hello.py | 1 +
 1 file changed, 1 insertion(+)
```

## Hallazgo registrado
Al vincular GitHub en Databricks Free Edition mediante cuenta enlazada / token, es necesario autorizar la aplicación **Databricks GitHub App** sobre el repositorio (o asegurar el alcance `Contents: Read and write` en la credencial seleccionada en la pestaña *Settings* del modal de Git) para permitir operaciones `git push` desde el Workspace.
