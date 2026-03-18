from pathlib import Path

from typer.testing import CliRunner

from girbridge.cli.app import app


class _FakeResult:
    def __init__(self, output_prompt_path: Path) -> None:
        self.output_prompt_path = output_prompt_path


class _FakeRegenerateCodegenPromptService:
    def __init__(self, config) -> None:  # noqa: ANN001
        self.config = config

    def generate_regenerate_code_prompt(
        self,
        mapping_delta_path: Path,
        existing_transformer_path: Path,
        output_prompt_path: Path,
        customer_name: str,
        mapping_file_path: Path | None = None,
        source_sample_xml_path: Path | None = None,
        xsd_path: Path | None = None,
    ) -> _FakeResult:
        assert mapping_delta_path.exists()
        assert existing_transformer_path.exists()
        assert customer_name == "CustomerA"
        assert mapping_file_path is not None and mapping_file_path.exists()
        assert source_sample_xml_path is not None and source_sample_xml_path.exists()
        assert xsd_path is not None and xsd_path.exists()
        return _FakeResult(output_prompt_path=output_prompt_path)


def test_regenerate_code_prompt_cli_command_runs(monkeypatch, tmp_path: Path) -> None:  # noqa: ANN001
    monkeypatch.setattr(
        "girbridge.cli.regenerate_code_prompt.RegenerateCodegenPromptService",
        _FakeRegenerateCodegenPromptService,
    )

    mapping_delta = tmp_path / "delta.yaml"
    mapping_delta.write_text("changes: []\n", encoding="utf-8")

    existing_transformer = tmp_path / "transformer.py"
    existing_transformer.write_text("def transform_xml(a, b):\n    pass\n", encoding="utf-8")

    mapping_file = tmp_path / "mapping.yaml"
    mapping_file.write_text("fields: []\n", encoding="utf-8")

    source_sample = tmp_path / "sample.xml"
    source_sample.write_text("<sample />", encoding="utf-8")

    xsd_file = tmp_path / "schema.xsd"
    xsd_file.write_text("<xsd />", encoding="utf-8")

    output_prompt = tmp_path / "prompt.txt"

    runner = CliRunner()
    result = runner.invoke(
        app,
        [
            "regenerate-code-prompt",
            "--mapping-delta",
            str(mapping_delta),
            "--existing-transformer",
            str(existing_transformer),
            "--output-prompt",
            str(output_prompt),
            "--mapping-file",
            str(mapping_file),
            "--source-sample-xml",
            str(source_sample),
            "--xsd-path",
            str(xsd_file),
            "--customer-name",
            "CustomerA",
        ],
    )

    assert result.exit_code == 0
    assert "Prompt written to:" in result.stdout
