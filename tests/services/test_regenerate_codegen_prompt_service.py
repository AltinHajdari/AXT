from pathlib import Path

import pytest

from girbridge.core.config import AppConfig
from girbridge.core.exceptions import PromptFileNotFoundError
from girbridge.services.regenerate_codegen_prompt_service import RegenerateCodegenPromptService

TEST_PROMPT_FILE = "resources/prompts/regenerate_code_system.txt"


class _FakeResourcePath:
    def __init__(self, text: str | None = None, missing: bool = False) -> None:
        self._text = text
        self._missing = missing

    def read_text(self, encoding: str = "utf-8") -> str:
        assert encoding == "utf-8"
        if self._missing:
            raise FileNotFoundError("missing")
        assert self._text is not None
        return self._text


class _FakeResourceRoot:
    def __init__(self, resource: _FakeResourcePath) -> None:
        self._resource = resource

    def joinpath(self, path: str) -> _FakeResourcePath:
        assert path
        return self._resource


def test_load_prompt_template_from_packaged_resource(monkeypatch: pytest.MonkeyPatch) -> None:
    service = RegenerateCodegenPromptService(
        config=AppConfig(draft_mapping_prompt_file=TEST_PROMPT_FILE)
    )
    fake_resource = _FakeResourcePath(text="SYSTEM TEMPLATE")

    monkeypatch.setattr(
        "girbridge.services.regenerate_codegen_prompt_service.resources.files",
        lambda package: _FakeResourceRoot(fake_resource),
    )

    assert service._load_prompt_template() == "SYSTEM TEMPLATE"


def test_load_prompt_template_raises_custom_error_when_missing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    service = RegenerateCodegenPromptService(
        config=AppConfig(draft_mapping_prompt_file="resources/prompts/missing.txt")
    )
    fake_resource = _FakeResourcePath(missing=True)

    monkeypatch.setattr(
        "girbridge.services.regenerate_codegen_prompt_service.resources.files",
        lambda package: _FakeResourceRoot(fake_resource),
    )

    with pytest.raises(PromptFileNotFoundError, match="missing.txt"):
        service._load_prompt_template()


def test_generate_regenerate_code_prompt_writes_output_and_attachments(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    service = RegenerateCodegenPromptService(
        config=AppConfig(draft_mapping_prompt_file=TEST_PROMPT_FILE)
    )
    monkeypatch.setattr(service, "_load_prompt_template", lambda: "PROMPT TEMPLATE")

    mapping_delta = tmp_path / "delta.yaml"
    mapping_delta.write_text("changes: []\n", encoding="utf-8")

    existing_transformer = tmp_path / "transformer.py"
    existing_transformer.write_text("def transform_xml(a, b):\n    pass\n", encoding="utf-8")

    mapping_file = tmp_path / "mapping.yaml"
    mapping_file.write_text("fields: []\n", encoding="utf-8")

    source_sample = tmp_path / "sample.xml"
    source_sample.write_text("<sample/>", encoding="utf-8")

    xsd_dir = tmp_path / "xsds"
    xsd_dir.mkdir()
    xsd_file = xsd_dir / "schema.xsd"
    xsd_file.write_text("<xsd />", encoding="utf-8")

    output_prompt = tmp_path / "out" / "prompt.txt"

    result = service.generate_regenerate_code_prompt(
        mapping_delta_path=mapping_delta,
        existing_transformer_path=existing_transformer,
        output_prompt_path=output_prompt,
        customer_name="Globex",
        mapping_file_path=mapping_file,
        source_sample_xml_path=source_sample,
        xsd_path=xsd_dir,
    )

    assert result.output_prompt_path == output_prompt
    assert output_prompt.exists()

    written = output_prompt.read_text(encoding="utf-8")
    assert "PROMPT TEMPLATE" in written
    assert "Globex" in written
    assert "- Mapping delta file: delta.yaml" in written
    assert "- Existing transformer code: transformer.py" in written
    assert "- Full mapping file (optional): mapping.yaml" in written

    attachments_dir = output_prompt.parent / "attachments"
    assert (attachments_dir / "delta.yaml").exists()
    assert (attachments_dir / "transformer.py").exists()
    assert (attachments_dir / "mapping.yaml").exists()
    assert (attachments_dir / "sample.xml").exists()
    assert (attachments_dir / "schema.xsd").exists()
