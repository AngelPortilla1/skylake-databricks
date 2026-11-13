"""Ingesta incremental de snapshots de OpenSky Network hacia Unity Catalog Volume."""

import io
import os
import sys

import requests
from databricks.sdk import WorkspaceClient
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

API_URL = "https://opensky-network.org/api/states/all"
TOKEN_URL = (
    "https://auth.opensky-network.org/auth/realms/opensky-network"
    "/protocol/openid-connect/token"
)
# Bounding box acotado para America Latina (reduce consumo de creditos y volumen)
BBOX = {"lamin": -56.0, "lomin": -120.0, "lamax": 33.0, "lomax": -30.0}
VOLUME_DIR = "/Volumes/skylake/bronze/landing/opensky/states"


def build_session() -> requests.Session:
    """Crea una sesion HTTP con reintentos exponenciales ante errores transitorios."""
    retry = Retry(
        total=5,
        backoff_factor=2,
        status_forcelist=[429, 500, 502, 503, 504],
        respect_retry_after_header=True,
    )
    session = requests.Session()
    session.mount("https://", HTTPAdapter(max_retries=retry))
    return session


def get_token(session: requests.Session) -> str | None:
    """Obtiene un token OAuth2 client_credentials de OpenSky si hay credenciales."""
    cid = os.getenv("OPENSKY_CLIENT_ID")
    secret = os.getenv("OPENSKY_CLIENT_SECRET")
    if not cid or not secret:
        return None  # acceso anonimo, con limites mas bajos
    response = session.post(
        TOKEN_URL,
        timeout=30,
        data={
            "grant_type": "client_credentials",
            "client_id": cid,
            "client_secret": secret,
        },
    )
    response.raise_for_status()
    return response.json()["access_token"]


def main() -> int:
    """Descarga el snapshot actual de OpenSky y lo sube al Volume de Bronze."""
    session = build_session()
    token = get_token(session)
    headers = {"Authorization": f"Bearer {token}"} if token else {}

    response = session.get(
        API_URL,
        params={**BBOX, "extended": 1},
        headers=headers,
        timeout=30,
    )
    response.raise_for_status()

    payload = response.json()
    ts = payload["time"]  # epoch del snapshot segun la API
    # Nombre determinista: re-ejecutar el mismo snapshot sobrescribe, no duplica
    path = f"{VOLUME_DIR}/states_{ts}.json"

    w = WorkspaceClient()  # usa DATABRICKS_HOST y DATABRICKS_TOKEN
    w.files.upload(path, io.BytesIO(response.content), overwrite=True)

    n = len(payload.get("states") or [])
    print(f"OK {path} ({n} estados)")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:
        print(f"ERROR: {type(exc).__name__}: {exc}", file=sys.stderr)
        sys.exit(1)
