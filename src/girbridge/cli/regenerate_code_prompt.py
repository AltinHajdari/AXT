from pathlib import Path

import typer
from rich.console import Console

from girbridge.core.config import AppConfig
from girbridge.services.regenerate_codegen_prompt_service import RegenerateCodegenPromptService

console = Console()


MAPPING_DELTA_FILE_OPTION = typer.Option(
    ...,
    "--mapping-delta",
    "-d",
    exists=True,
    file_okay=True,
    dir_okay=False,
    readable=True,
    help="Path to the mapping delta YAML file.",
)

EXISTING_TRANSFORMER_OPTION = typer.Option(
    ...,
    "--existing-transformer",
    "-t",
    exists=True,
    file_okay=True,
    dir_okay=False,
    readable=True,
    help="Path to existing transformer Python file to update incrementally.",
)

MAPPING_FILE_OPTION = typer.Option(
    None,
    "--mapping-file",
    "-m",
    exists=True,
    file_okay=True,
    dir_okay=False,
    readable=True,
    help="Optional path to full mapping YAML file for ambiguity resolution.",
)

OUTPUT_PROMPT_OPTION = typer.Option(
    ...,
    "--output-prompt",
    "-o",
    help="Output path for the generated regeneration prompt text file.",
)

SOURCE_SAMPLE_XML_OPTION = typer.Option(
    None,
    "--source-sample-xml",
    "-s",
    exists=True,
    file_okay=True,
    dir_okay=False,
    readable=True,
    help="Optional path to a representative source XML snippet.",
)

XSD_PATH_OPTION = typer.Option(
    None,
    "--xsd-path",
    "-x",
    exists=True,
    readable=True,
    help="Optional path to an XSD file or a directory containing XSD files.",
)

CUSTOMER_NAME_OPTION = typer.Option(
    "unknown_customer",
    "--customer-name",
    help="Customer identifier used in metadata.",
)


def regenerate_code_prompt_command(
    mapping_delta: Path = MAPPING_DELTA_FILE_OPTION,
    existing_transformer: Path = EXISTING_TRANSFORMER_OPTION,
    output_prompt: Path = OUTPUT_PROMPT_OPTION,
    mapping_file: Path | None = MAPPING_FILE_OPTION,
    source_sample_xml: Path | None = SOURCE_SAMPLE_XML_OPTION,
    xsd_path: Path | None = XSD_PATH_OPTION,
    customer_name: str = CUSTOMER_NAME_OPTION,
) -> None:
    """
    Generate an incremental code-regeneration prompt bundle using mapping delta and existing code.
    """
    config = AppConfig(draft_mapping_prompt_file="resources/prompts/regenerate_code_system.txt")
    service = RegenerateCodegenPromptService(config=config)

    console.print("[bold blue]Starting regenerate-code-prompt...[/bold blue]")

    result = service.generate_regenerate_code_prompt(
        mapping_delta_path=mapping_delta,
        existing_transformer_path=existing_transformer,
        output_prompt_path=output_prompt,
        customer_name=customer_name,
        mapping_file_path=mapping_file,
        source_sample_xml_path=source_sample_xml,
        xsd_path=xsd_path,
    )

    console.print(f"[green]Prompt written to:[/green] {result.output_prompt_path}")

    attachments_dir = result.output_prompt_path.parent / "attachments"

    console.print("")
    console.print("[bold yellow]Next steps:[/bold yellow]")
    console.print("1. Open your chatbot (ChatGPT, Copilot, etc.)")
    console.print(f"2. Upload all files from: {attachments_dir}")
    console.print(f"3. Paste the prompt from: {result.output_prompt_path}")
    console.print("")
