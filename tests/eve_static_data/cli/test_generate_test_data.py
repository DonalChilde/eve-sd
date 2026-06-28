"""Tests for dev fixture generation command."""

from pathlib import Path

from typer.testing import CliRunner

from eve_static_data.cli.dev.generate_test_data import app

runner = CliRunner()


def test_generate_yaml_model_includes_sde_metadata_file(tmp_path: Path) -> None:
    """YAML-model fixture generation should include _sde metadata output files."""
    sde_path = tmp_path / "sde_yaml"
    sde_path.mkdir(parents=True, exist_ok=True)
    (sde_path / "_sde.yaml").write_text(
        "sde:\n  buildNumber: 3400000\n  releaseDate: '2026-06-25T12:00:48Z'\n",
        encoding="utf-8",
    )
    (sde_path / "agentTypes.yaml").write_text(
        "1:\n  agentTypeID: 1\n  divisionID: 1\n",
        encoding="utf-8",
    )

    out_path = tmp_path / "fixtures_yaml"
    result = runner.invoke(app, [str(sde_path), str(out_path)])

    assert result.exit_code == 0
    assert (out_path / "yaml" / "_sde.yaml").exists()
    assert (out_path / "json" / "_sde.json").exists()


def test_generate_jsonl_model_includes_sde_metadata_file(tmp_path: Path) -> None:
    """JSONL-model fixture generation should include _sde.jsonl in output."""
    sde_path = tmp_path / "sde_jsonl"
    sde_path.mkdir(parents=True, exist_ok=True)
    (sde_path / "_sde.jsonl").write_text(
        '{"_key":"sde","buildNumber":3400000,"releaseDate":"2026-06-25T12:00:48Z"}\n',
        encoding="utf-8",
    )
    (sde_path / "dogmaAttributes.jsonl").write_text(
        '{"_key":1,"attributeID":1}\n{"_key":2,"attributeID":2}\n',
        encoding="utf-8",
    )

    out_path = tmp_path / "fixtures_jsonl"
    result = runner.invoke(app, [str(sde_path), str(out_path)])

    assert result.exit_code == 0
    assert (out_path / "_sde.jsonl").exists()


def test_generate_rejects_yaml_model_from_json_media(tmp_path: Path) -> None:
    """Fixture generation should reject YAML-model data exported as JSON media."""
    sde_path = tmp_path / "sde_yaml_json"
    sde_path.mkdir(parents=True, exist_ok=True)
    (sde_path / "_sde.json").write_text(
        '{"sde": {"buildNumber": 3400000, "releaseDate": "2026-06-25T12:00:48Z"}}',
        encoding="utf-8",
    )
    (sde_path / "agentTypes.json").write_text(
        '{"1": {"agentTypeID": 1, "divisionID": 1}}',
        encoding="utf-8",
    )

    out_path = tmp_path / "fixtures_yaml_json"
    result = runner.invoke(app, [str(sde_path), str(out_path)])

    assert result.exit_code == 2


def test_generate_rejects_jsonl_model_from_json_media(tmp_path: Path) -> None:
    """Fixture generation should reject JSONL-model data exported as JSON media."""
    sde_path = tmp_path / "sde_jsonl_json"
    sde_path.mkdir(parents=True, exist_ok=True)
    (sde_path / "_sde.json").write_text(
        '{"_key": "sde", "buildNumber": 3400000, "releaseDate": "2026-06-25T12:00:48Z"}',
        encoding="utf-8",
    )
    (sde_path / "dogmaAttributes.json").write_text(
        '{"1": {"attributeID": 1}, "2": {"attributeID": 2}}',
        encoding="utf-8",
    )

    out_path = tmp_path / "fixtures_jsonl_json"
    result = runner.invoke(app, [str(sde_path), str(out_path)])

    assert result.exit_code == 2
