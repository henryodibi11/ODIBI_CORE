"""
ODIBI CORE Command-Line Interface.

Provides convenient commands for running, validating, and documenting pipelines.

Usage:
    odibi run --config pipeline.json --engine pandas
    odibi validate --config pipeline.json
    odibi docs --output docs/
    odibi version
"""

import sys
import json
import logging
from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich import print as rprint

from odibi_core.__version__ import __version__, __phase__, __supported_engines__
from odibi_core.sdk import ODIBI, Pipeline
from odibi_core.sdk.config_validator import ConfigValidator

console = Console()
logger = logging.getLogger(__name__)


@click.group()
@click.version_option(__version__, prog_name="ODIBI CORE")
def main() -> None:
    """
    ODIBI CORE - Node-centric, config-driven data engineering framework.

    Execute pipelines, validate configs, and generate documentation.
    """
    pass


@main.command()
@click.option(
    "--config",
    "-c",
    required=True,
    type=click.Path(exists=True),
    help="Path to pipeline configuration (JSON, SQLite, or CSV)",
)
@click.option(
    "--engine",
    "-e",
    default="pandas",
    type=click.Choice(["pandas", "spark"], case_sensitive=False),
    help="Execution engine (default: pandas)",
)
@click.option(
    "--workers",
    "-w",
    default=4,
    type=int,
    help="Maximum parallel workers (default: 4)",
)
@click.option(
    "--secrets",
    "-s",
    type=str,
    help="Secrets as JSON string or path to JSON file",
)
@click.option(
    "--project",
    "-p",
    type=str,
    help="Project name filter (for SQLite configs)",
)
@click.option(
    "--verbose",
    "-v",
    is_flag=True,
    help="Enable verbose logging",
)
def run(
    config: str,
    engine: str,
    workers: int,
    secrets: Optional[str],
    project: Optional[str],
    verbose: bool,
) -> None:
    """
    Execute a pipeline from configuration file.

    Examples:
        odibi run --config pipeline.json --engine pandas
        odibi run -c config.db -e spark -w 8
        odibi run -c pipeline.json --secrets '{"db_pass": "secret"}'
    """
    # Setup logging
    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # Parse secrets
    secrets_dict = {}
    if secrets:
        if Path(secrets).exists():
            with open(secrets, "r") as f:
                secrets_dict = json.load(f)
        else:
            try:
                secrets_dict = json.loads(secrets)
            except json.JSONDecodeError:
                console.print("[red]Error: Invalid secrets format[/red]")
                sys.exit(1)

    # Display header
    console.print("\n[bold cyan]ODIBI CORE Pipeline Execution[/bold cyan]")
    console.print(f"Version: {__version__} ({__phase__})")
    console.print(f"Config: {config}")
    console.print(f"Engine: {engine.upper()}")
    console.print(f"Workers: {workers}\n")

    # Execute pipeline
    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Loading configuration...", total=None)

            # Load config
            kwargs = {"project": project} if project else {}
            pipeline = Pipeline.from_config(config, **kwargs)
            pipeline.set_engine(engine).set_secrets(secrets_dict).set_parallelism(
                workers
            )

            progress.update(task, description="Executing pipeline...")

            # Execute
            result = pipeline.execute()

        # Display results
        console.print("\n[bold green]Pipeline Execution Complete[/bold green]\n")

        # Create results table
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", justify="right")

        table.add_row("Status", "✅ SUCCESS" if result.is_success() else "❌ FAILED")
        table.add_row("Success Count", str(result.success_count))
        table.add_row("Failed Count", str(result.failed_count))
        table.add_row("Total Duration", f"{result.total_duration_ms:.2f}ms")
        table.add_row(
            "Avg Node Duration",
            f"{result.total_duration_ms / len(result.results):.2f}ms",
        )

        console.print(table)

        # Exit code
        sys.exit(0 if result.is_success() else 1)

    except Exception as e:
        console.print(f"\n[bold red]Error:[/bold red] {str(e)}")
        if verbose:
            console.print_exception()
        sys.exit(1)


@main.command()
@click.option(
    "--config",
    "-c",
    required=True,
    type=click.Path(exists=True),
    help="Path to pipeline configuration",
)
@click.option(
    "--strict",
    is_flag=True,
    help="Fail on warnings (not just errors)",
)
def validate(config: str, strict: bool) -> None:
    """
    Validate a pipeline configuration file.

    Checks for:
    - Required fields (layer, name, type)
    - Valid layers and engines
    - Duplicate step names
    - Circular dependencies
    - Valid JSON in inputs/outputs

    Examples:
        odibi validate --config pipeline.json
        odibi validate -c config.db --strict
    """
    console.print("\n[bold cyan]ODIBI CORE Config Validator[/bold cyan]")
    console.print(f"Config: {config}")
    console.print(f"Mode: {'STRICT' if strict else 'NORMAL'}\n")

    validator = ConfigValidator()

    try:
        is_valid = validator.validate(config, strict=strict)

        # Print issues
        if validator.issues:
            console.print(f"[yellow]Found {len(validator.issues)} issue(s):[/yellow]\n")
            for issue in validator.issues:
                console.print(str(issue))
            console.print()

        # Print summary
        summary = validator.get_summary()
        if is_valid:
            console.print(f"[bold green]{summary}[/bold green]")
            sys.exit(0)
        else:
            console.print(f"[bold red]{summary}[/bold red]")
            sys.exit(1)

    except Exception as e:
        console.print(f"[bold red]Validation Error:[/bold red] {str(e)}")
        sys.exit(1)


@main.command()
@click.option(
    "--output",
    "-o",
    default="docs",
    type=click.Path(),
    help="Output directory for documentation (default: docs/)",
)
@click.option(
    "--format",
    "-f",
    default="markdown",
    type=click.Choice(["markdown", "html"], case_sensitive=False),
    help="Documentation format (default: markdown)",
)
def docs(output: str, format: str) -> None:
    """
    Generate documentation from docstrings.

    Auto-generates API documentation from Python docstrings.

    Examples:
        odibi docs --output docs/
        odibi docs -o api_docs -f html
    """
    from odibi_core.sdk.doc_generator import DocGenerator

    console.print("\n[bold cyan]ODIBI CORE Documentation Generator[/bold cyan]")
    console.print(f"Output: {output}")
    console.print(f"Format: {format.upper()}\n")

    try:
        generator = DocGenerator(output_dir=output, format=format)
        count = generator.generate()

        console.print(
            f"\n[bold green]✅ Generated {count} documentation files[/bold green]"
        )
        console.print(f"Location: {Path(output).absolute()}")

    except ImportError:
        console.print(
            "[yellow]⚠️  Doc generator not yet implemented. Coming in Phase 10.[/yellow]"
        )
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        sys.exit(1)


@main.command()
def version() -> None:
    """
    Display version and environment information.
    """
    console.print("\n[bold cyan]ODIBI CORE[/bold cyan]")
    console.print(f"Version: [bold]{__version__}[/bold]")
    console.print(f"Phase: {__phase__}")
    console.print(f"Supported Engines: {', '.join(__supported_engines__)}")

    # Load manifest
    try:
        manifest_path = Path(__file__).parent.parent / "manifest.json"
        if manifest_path.exists():
            with open(manifest_path, "r") as f:
                manifest = json.load(f)
                console.print(f"\nFeatures:")
                for feature, enabled in manifest.get("features", {}).items():
                    icon = "✅" if enabled else "❌"
                    console.print(f"  {icon} {feature.replace('_', ' ').title()}")
    except Exception:
        pass

    console.print()


@main.command()
@click.option(
    "--config",
    "-c",
    required=True,
    type=click.Path(exists=True),
    help="Path to pipeline configuration",
)
@click.option(
    "--output",
    "-o",
    type=click.Path(),
    help="Output file for visualization (SVG or PNG)",
)
def visualize(config: str, output: Optional[str]) -> None:
    """
    Visualize pipeline DAG.

    Generates a visual representation of the pipeline structure.

    Examples:
        odibi visualize --config pipeline.json
        odibi visualize -c pipeline.json -o dag.svg
    """
    console.print("[yellow]⚠️  DAG visualization coming in Phase 10[/yellow]")


if __name__ == "__main__":
    main()
