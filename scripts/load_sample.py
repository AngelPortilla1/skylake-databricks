"""Carga el dataset de muestra local (Plan B) hacia el Unity Catalog Volume de SkyLake."""

from __future__ import annotations

import argparse
import io
import os
import sys
from pathlib import Path

from databricks.sdk import WorkspaceClient
from databricks.sdk.errors import NotFound

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover - fallback cuando solo se instala requirements-ingest.txt
    load_dotenv = None

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SAMPLE_DIR = REPO_ROOT / "data" / "sample"
DEFAULT_VOLUME_ROOT = "/Volumes/skylake/bronze/landing"


def list_existing_files(client: WorkspaceClient, remote_dir: str) -> set[str]:
    """Devuelve los nombres de archivo ya presentes en un directorio del Volume."""
    try:
        entries = client.files.list_directory_contents(remote_dir)
        return {entry.name for entry in entries if entry.name and not entry.is_directory}
    except NotFound:
        return set()


def upload_files(
    client: WorkspaceClient,
    local_files: list[Path],
    remote_dir: str,
    overwrite: bool = False,
) -> tuple[int, int]:
    """Sube una lista de archivos locales a un subdirectorio del Volume."""
    existing = set() if overwrite else list_existing_files(client, remote_dir)
    uploaded = 0
    skipped = 0

    for file_path in sorted(local_files):
        if not overwrite and file_path.name in existing:
            print(f"SKIP {remote_dir}/{file_path.name} (ya existe en el Volume)")
            skipped += 1
            continue

        remote_path = f"{remote_dir}/{file_path.name}"
        payload = file_path.read_bytes()
        client.files.upload(remote_path, io.BytesIO(payload), overwrite=True)
        print(f"OK   {remote_path} ({len(payload):,} bytes)")
        uploaded += 1

    return uploaded, skipped


def load_sample_dataset(
    client: WorkspaceClient,
    sample_dir: Path = DEFAULT_SAMPLE_DIR,
    volume_root: str = DEFAULT_VOLUME_ROOT,
    overwrite: bool = False,
) -> dict[str, int]:
    """Carga los snapshots JSON de OpenSky y los CSV de referencia de aeronaves al Volume."""
    volume_root = volume_root.rstrip("/")
    state_files = sorted(sample_dir.glob("states_*.json"))
    aircraft_dir = sample_dir / "reference" / "aircraft"
    aircraft_files = sorted(aircraft_dir.glob("aircraft_*.csv")) if aircraft_dir.exists() else []

    if not state_files:
        raise FileNotFoundError(
            f"No se encontraron snapshots 'states_*.json' en {sample_dir}"
        )

    states_uploaded, states_skipped = upload_files(
        client=client,
        local_files=state_files,
        remote_dir=f"{volume_root}/opensky/states",
        overwrite=overwrite,
    )

    ref_uploaded, ref_skipped = 0, 0
    if aircraft_files:
        ref_uploaded, ref_skipped = upload_files(
            client=client,
            local_files=aircraft_files,
            remote_dir=f"{volume_root}/reference/aircraft",
            overwrite=overwrite,
        )

    return {
        "states_uploaded": states_uploaded,
        "states_skipped": states_skipped,
        "reference_uploaded": ref_uploaded,
        "reference_skipped": ref_skipped,
    }


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parsea los argumentos de linea de comandos."""
    parser = argparse.Namespace
    cli = argparse.ArgumentParser(
        description="Sube el dataset de muestra (Plan B) al Volume de Databricks."
    )
    cli.add_argument(
        "--sample-dir",
        type=Path,
        default=DEFAULT_SAMPLE_DIR,
        help="Directorio local con los archivos de muestra (default: data/sample).",
    )
    cli.add_argument(
        "--volume-root",
        type=str,
        default=DEFAULT_VOLUME_ROOT,
        help="Ruta base del Volume en Unity Catalog (default: /Volumes/skylake/bronze/landing).",
    )
    cli.add_argument(
        "--overwrite",
        action="store_true",
        help="Sobrescribe archivos aunque ya existan en el Volume.",
    )
    parser = cli.parse_args(argv)
    return parser


def build_workspace_client() -> WorkspaceClient:
    """Construye WorkspaceClient priorizando DATABRICKS_HOST y DATABRICKS_TOKEN si existen."""
    host = os.getenv("DATABRICKS_HOST")
    token = os.getenv("DATABRICKS_TOKEN")
    if host and token:
        return WorkspaceClient(host=host, token=token)
    return WorkspaceClient()


def main(argv: list[str] | None = None) -> int:
    """Punto de entrada principal del script."""
    if load_dotenv is not None:
        load_dotenv(REPO_ROOT / ".env")

    args = parse_args(argv)
    client = build_workspace_client()
    summary = load_sample_dataset(
        client=client,
        sample_dir=args.sample_dir,
        volume_root=args.volume_root,
        overwrite=args.overwrite,
    )
    print(
        "Resumen Plan B -> "
        f"states subidos: {summary['states_uploaded']} "
        f"(omitidos: {summary['states_skipped']}), "
        f"referencia subida: {summary['reference_uploaded']} "
        f"(omitidos: {summary['reference_skipped']})"
    )
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:  # noqa: BLE001
        print(f"ERROR: {type(exc).__name__}: {exc}", file=sys.stderr)
        sys.exit(1)
