from importlib import resources
from pathlib import Path

from girbridge.adapters.storage import FileStorage
from girbridge.core.config import AppConfig
from girbridge.core.exceptions import PromptFileNotFoundError
from girbridge.core.models import GenerateCodePromptResult


class RegenerateCodegenPromptService:
    def __init__(self, config: AppConfig) -> None:
        self.config = config
        self.storage = FileStorage()

    def generate_regenerate_code_prompt(
        self,
        mapping_delta_path: Path,
        existing_transformer_path: Path,
        output_prompt_path: Path,
        customer_name: str,
        mapping_file_path: Path | None = None,
        source_sample_xml_path: Path | None = None,
        xsd_path: Path | None = None,
    ) -> GenerateCodePromptResult:
        prompt_template = self._load_prompt_template()

        attachments_dir = output_prompt_path.parent / "attachments"
        attachments_dir.mkdir(parents=True, exist_ok=True)

        attached_files: list[str] = []

        delta_target = attachments_dir / mapping_delta_path.name
        self.storage.copy_file(mapping_delta_path, delta_target)
        attached_files.append(delta_target.name)

        transformer_target = attachments_dir / existing_transformer_path.name
        self.storage.copy_file(existing_transformer_path, transformer_target)
        attached_files.append(transformer_target.name)

        mapping_target_name: str | None = None
        if mapping_file_path:
            mapping_target = attachments_dir / mapping_file_path.name
            self.storage.copy_file(mapping_file_path, mapping_target)
            attached_files.append(mapping_target.name)
            mapping_target_name = mapping_target.name

        if source_sample_xml_path:
            source_target = attachments_dir / source_sample_xml_path.name
            self.storage.copy_file(source_sample_xml_path, source_target)
            attached_files.append(source_target.name)

        if xsd_path:
            xsd_files = self._copy_xsd_attachments(
                xsd_path=xsd_path, attachments_dir=attachments_dir
            )
            attached_files.extend(xsd_files)

        prompt = self._build_prompt(
            prompt_template=prompt_template,
            customer_name=customer_name,
            mapping_delta_file_name=delta_target.name,
            existing_transformer_file_name=transformer_target.name,
            attached_files=attached_files,
            mapping_file_name=mapping_target_name,
        )

        self.storage.write_text(output_prompt_path, prompt)

        return GenerateCodePromptResult(output_prompt_path=output_prompt_path)

    def _load_prompt_template(self) -> str:
        resource_path = resources.files("girbridge").joinpath(self.config.draft_mapping_prompt_file)

        try:
            return resource_path.read_text(encoding="utf-8")
        except FileNotFoundError as error:
            raise PromptFileNotFoundError(
                f"Prompt file not found: {self.config.draft_mapping_prompt_file}"
            ) from error

    def _copy_xsd_attachments(
        self,
        xsd_path: Path,
        attachments_dir: Path,
    ) -> list[str]:
        copied_files: list[str] = []

        if xsd_path.is_file():
            target = attachments_dir / xsd_path.name
            self.storage.copy_file(xsd_path, target)
            copied_files.append(target.name)
            return copied_files

        xsd_files = sorted(xsd_path.rglob("*.xsd"))

        for file_path in xsd_files:
            target = attachments_dir / file_path.name
            self.storage.copy_file(file_path, target)
            copied_files.append(target.name)

        return copied_files

    def _build_prompt(
        self,
        prompt_template: str,
        customer_name: str,
        mapping_delta_file_name: str,
        existing_transformer_file_name: str,
        attached_files: list[str],
        mapping_file_name: str | None,
    ) -> str:
        parts: list[str] = []

        parts.append(prompt_template)

        parts.append("\n\n## CUSTOMER\n")
        parts.append(customer_name)

        parts.append("\n\n## ATTACHED FILES\n")
        parts.append("The following files are attached to this conversation and must be used.\n")

        for file_name in sorted(set(attached_files)):
            parts.append("- " + file_name + "\n")

        parts.append("\n## REQUIRED INPUT FILES\n")
        parts.append("- Mapping delta file: " + mapping_delta_file_name + "\n")
        parts.append("- Existing transformer code: " + existing_transformer_file_name + "\n")
        if mapping_file_name:
            parts.append("- Full mapping file (optional): " + mapping_file_name + "\n")

        return "".join(parts)
