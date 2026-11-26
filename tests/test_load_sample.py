"""Pruebas unitarias para el cargador del dataset de muestra (SKY-015)."""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from databricks.sdk.errors import NotFound

from scripts.load_sample import load_sample_dataset


def _build_sample_tree(tmp_path: Path) -> Path:
    sample_dir = tmp_path / "sample"
    ref_dir = sample_dir / "reference" / "aircraft"
    ref_dir.mkdir(parents=True)

    (sample_dir / "states_1795000001.json").write_text('{"time": 1795000001, "states": []}', encoding="utf-8")
    (sample_dir / "states_1795000002.json").write_text('{"time": 1795000002, "states": []}', encoding="utf-8")
    (ref_dir / "aircraft_2026_11.csv").write_text("icao24,operator_name\nabc123,LATAM\n", encoding="utf-8")
    (ref_dir / "aircraft_2026_12.csv").write_text("icao24,operator_name\nabc123,LATAM (Updated)\n", encoding="utf-8")
    return sample_dir


def test_load_sample_dataset_uploads_all_into_empty_volume(tmp_path: Path) -> None:
    sample_dir = _build_sample_tree(tmp_path)
    client = MagicMock()
    client.files.list_directory_contents.side_effect = NotFound("Directory does not exist")

    summary = load_sample_dataset(
        client=client,
        sample_dir=sample_dir,
        volume_root="/Volumes/skylake/bronze/landing",
        overwrite=False,
    )

    assert summary == {
        "states_uploaded": 2,
        "states_skipped": 0,
        "reference_uploaded": 2,
        "reference_skipped": 0,
    }
    uploaded_paths = [call.args[0] for call in client.files.upload.call_args_list]
    assert uploaded_paths == [
        "/Volumes/skylake/bronze/landing/opensky/states/states_1795000001.json",
        "/Volumes/skylake/bronze/landing/opensky/states/states_1795000002.json",
        "/Volumes/skylake/bronze/landing/reference/aircraft/aircraft_2026_11.csv",
        "/Volumes/skylake/bronze/landing/reference/aircraft/aircraft_2026_12.csv",
    ]


def test_load_sample_dataset_skips_existing_unless_overwrite(tmp_path: Path) -> None:
    sample_dir = _build_sample_tree(tmp_path)
    client = MagicMock()

    def fake_list(remote_dir: str):
        if remote_dir.endswith("/opensky/states"):
            return [SimpleNamespace(name="states_1795000001.json", is_directory=False)]
        if remote_dir.endswith("/reference/aircraft"):
            return [
                SimpleNamespace(name="aircraft_2026_11.csv", is_directory=False),
                SimpleNamespace(name="aircraft_2026_12.csv", is_directory=False),
            ]
        return []

    client.files.list_directory_contents.side_effect = fake_list

    summary = load_sample_dataset(
        client=client,
        sample_dir=sample_dir,
        volume_root="/Volumes/skylake/bronze/landing",
        overwrite=False,
    )

    assert summary == {
        "states_uploaded": 1,
        "states_skipped": 1,
        "reference_uploaded": 0,
        "reference_skipped": 2,
    }
    uploaded_paths = [call.args[0] for call in client.files.upload.call_args_list]
    assert uploaded_paths == [
        "/Volumes/skylake/bronze/landing/opensky/states/states_1795000002.json",
    ]


def test_load_sample_dataset_raises_when_missing_states(tmp_path: Path) -> None:
    empty_dir = tmp_path / "empty"
    empty_dir.mkdir()
    client = MagicMock()

    with pytest.raises(FileNotFoundError, match="states_\\*\\.json"):
        load_sample_dataset(client=client, sample_dir=empty_dir)
