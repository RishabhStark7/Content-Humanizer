"""Command Line Interface for Human Writing Engine."""

import asyncio
from pathlib import Path
import click
import yaml
from rich.console import Console
from rich.panel import Panel

from schemas.brief import ContentBriefModel
from src.ingestion.router import parse_document
from src.planner.brief_planner import prepare_plan_from_brief
from src.planner.outline_generator import generate_outline_document
from src.generation.variant_generator import generate_10_variants
from src.diversity.filter import filter_most_diverse_variants
from src.reconstruction.engine import reconstruct_article
from src.style.cliche_cleaner import clean_ai_cliches
from src.style.readability import optimize_document_readability
from src.validation.engine import validate_article
from src.exporters.docx_exporter import export_to_docx
from src.exporters.md_exporter import export_to_markdown
from src.exporters.html_exporter import export_to_html
from src.exporters.json_exporter import export_to_json
from src.exporters.excel_exporter import export_to_excel

console = Console()


@click.group()
def cli():
    """Human Writing Engine CLI."""
    pass


@cli.command("process-doc")
@click.option("--input", "-i", required=True, type=click.Path(exists=True), help="Input document path (docx, md, html, txt)")
@click.option("--output-dir", "-o", default="./output", help="Output directory")
def process_doc(input: str, output_dir: str):
    """Process an existing document through the editorial pipeline (Mode A)."""
    console.print(Panel(f"[bold green]Human Writing Engine[/bold green]\nProcessing document: [yellow]{input}[/yellow]"))

    in_path = Path(input)
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    # 1. Ingestion
    console.print("[blue]Step 1/7:[/blue] Parsing document...")
    doc = parse_document(in_path)

    # 2. Outline / Baseline Alignment
    console.print("[blue]Step 2/7:[/blue] Aligning outline structure...")
    doc = generate_outline_document(doc)

    # 3. Generate 10 Variants
    console.print("[blue]Step 3/7:[/blue] Generating 10 editorial persona variants via Vertex AI...")
    variants = asyncio.run(generate_10_variants(doc))

    # 4. Diversity Analysis (Keep 7, Discard 3)
    console.print("[blue]Step 4/7:[/blue] Running diversity filter (discarding 3 most redundant)...")
    retained_variants, div_report = filter_most_diverse_variants(variants, retain_count=7)
    console.print(f"  Retained personas: {', '.join(div_report.retained_persona_ids)}")
    console.print(f"  Discarded personas: {', '.join(div_report.discarded_persona_ids)}")

    # 5. Local Deterministic Reconstruction (Pure Python)
    console.print("[blue]Step 5/7:[/blue] Reconstructing article with Local Human Reconstruction Engine (0 LLM calls)...")
    reconstructed_doc = reconstruct_article(retained_variants, doc)

    # 6. Style Refinement & Validation
    console.print("[blue]Step 6/7:[/blue] Applying style refinement and validating guardrails...")
    reconstructed_doc.raw_content = clean_ai_cliches(reconstructed_doc.raw_content)
    reconstructed_doc = optimize_document_readability(reconstructed_doc, target_body_words=doc.total_word_count)
    val_report = validate_article(reconstructed_doc, target_word_count=doc.total_word_count)

    # 7. Multi-Format Export
    console.print("[blue]Step 7/7:[/blue] Exporting publication-ready files and Excel quality report...")
    stem = in_path.stem
    export_to_docx(reconstructed_doc, out_dir / f"{stem}_humanized.docx", val_report)
    export_to_markdown(reconstructed_doc, out_dir / f"{stem}_humanized.md", val_report)
    export_to_html(reconstructed_doc, out_dir / f"{stem}_humanized.html", val_report)
    export_to_json(reconstructed_doc, out_dir / f"{stem}_humanized.json", val_report)
    export_to_excel(reconstructed_doc, out_dir / f"{stem}_quality_markers.xlsx", val_report, div_report)

    console.print(f"[bold green][OK] Done![/bold green] Exported DOCX, Markdown, HTML, JSON, and Excel markers to [yellow]{out_dir}[/yellow]")


@cli.command("process-brief")
@click.option("--brief", "-b", required=True, type=click.Path(exists=True), help="Content brief YAML file path")
@click.option("--output-dir", "-o", default="./output", help="Output directory")
def process_brief(brief: str, output_dir: str):
    """Generate a publication-ready article from a content brief (Mode B)."""
    console.print(Panel(f"[bold green]Human Writing Engine[/bold green]\nGenerating from brief: [yellow]{brief}[/yellow]"))

    brief_path = Path(brief)
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    with open(brief_path, "r", encoding="utf-8") as f:
        brief_data = yaml.safe_load(f)

    brief_model = ContentBriefModel(**brief_data)

    # 1. Plan baseline from brief
    console.print("[blue]Step 1/7:[/blue] Planning article outline from brief...")
    doc = prepare_plan_from_brief(brief_model)

    # 2. Outline refinement
    doc = generate_outline_document(doc)

    # 3. Generate 10 Variants
    console.print("[blue]Step 3/7:[/blue] Generating 10 editorial persona variants via Vertex AI...")
    variants = asyncio.run(generate_10_variants(doc))

    # 4. Diversity Analysis
    console.print("[blue]Step 4/7:[/blue] Filtering top 7 most diverse variants...")
    retained_variants, div_report = filter_most_diverse_variants(variants, retain_count=7)

    # 5. Local Reconstruction
    console.print("[blue]Step 5/7:[/blue] Synthesizing cohesive article via Human Reconstruction Engine...")
    reconstructed_doc = reconstruct_article(retained_variants, doc)

    # 6. Style Refinement & Validation
    console.print("[blue]Step 6/7:[/blue] Cleaning clichés and validating editorial guardrails...")
    reconstructed_doc.raw_content = clean_ai_cliches(reconstructed_doc.raw_content)
    reconstructed_doc = optimize_document_readability(reconstructed_doc, target_body_words=brief_model.target_word_count)
    val_report = validate_article(reconstructed_doc, target_word_count=brief_model.target_word_count)

    # 7. Multi-Format Export
    console.print("[blue]Step 7/7:[/blue] Exporting publication-ready outputs and Excel report...")
    stem = brief_path.stem
    export_to_docx(reconstructed_doc, out_dir / f"{stem}_article.docx", val_report)
    export_to_markdown(reconstructed_doc, out_dir / f"{stem}_article.md", val_report)
    export_to_html(reconstructed_doc, out_dir / f"{stem}_article.html", val_report)
    export_to_json(reconstructed_doc, out_dir / f"{stem}_article.json", val_report)
    export_to_excel(reconstructed_doc, out_dir / f"{stem}_quality_markers.xlsx", val_report, div_report)

    console.print(f"[bold green][OK] Done![/bold green] Generated files and Excel report exported to [yellow]{out_dir}[/yellow]")


if __name__ == "__main__":
    cli()
