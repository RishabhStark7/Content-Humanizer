"""Command Line Interface for Human Writing Engine."""

import asyncio
from pathlib import Path
import click
import yaml
from rich.console import Console
from rich.panel import Panel

from schemas.brief import ContentBriefModel
from schemas.document import DocumentModel
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


def save_variant_documents(retained_variants, variants_dir: Path, drafts_dir: Path):
    """Save all 7 retained AI variant documents as DOCX & Markdown files in output/variants/ and output/drafts/."""
    variants_dir.mkdir(parents=True, exist_ok=True)
    drafts_dir.mkdir(parents=True, exist_ok=True)

    # Save 7 retained variant DOCX files
    for idx, v in enumerate(retained_variants, 1):
        # Convert variant string into DocumentModel for docx export
        v_doc = parse_document_text(v.raw_text, title=f"Variant {idx}: {v.persona_name}")
        doc_filename = f"Variant_{idx}_{v.persona_id}.docx"
        md_filename = f"Variant_{idx}_{v.persona_id}.md"

        export_to_docx(v_doc, variants_dir / doc_filename)
        (variants_dir / md_filename).write_text(v.raw_text, encoding="utf-8")
        (drafts_dir / md_filename).write_text(v.raw_text, encoding="utf-8")


def parse_document_text(text: str, title: str) -> DocumentModel:
    """Helper to convert raw variant text into DocumentModel for DOCX export."""
    from schemas.document import DocumentModel, Section
    sections = []
    current_heading = title
    current_lines = []

    for line in text.splitlines():
        if line.startswith("## "):
            if current_lines:
                sections.append(Section(heading=current_heading, level=2, content="\n".join(current_lines), word_count=len("\n".join(current_lines).split())))
                current_lines = []
            current_heading = line.replace("## ", "").strip()
        else:
            current_lines.append(line)

    if current_lines:
        sections.append(Section(heading=current_heading, level=2, content="\n".join(current_lines), word_count=len("\n".join(current_lines).split())))

    return DocumentModel(
        title=title,
        metadata={},
        sections=sections,
        faqs=[],
        original_format="md",
        total_word_count=len(text.split()),
        raw_content=text
    )


@cli.command("process-doc")
@click.option("--input", "-i", default=None, help="Input document path (defaults to auto-scanning input/ folder)")
@click.option("--output-dir", "-o", default="./output", help="Output root directory")
def process_doc(input: str, output_dir: str):
    """Process an existing document through the editorial pipeline (Mode A)."""
    out_root = Path(output_dir)
    final_doc_dir = out_root / "final_doc"
    variants_dir = out_root / "variants"
    drafts_dir = out_root / "drafts"

    final_doc_dir.mkdir(parents=True, exist_ok=True)
    variants_dir.mkdir(parents=True, exist_ok=True)
    drafts_dir.mkdir(parents=True, exist_ok=True)

    # Auto-scan input/ folder if input is not specified
    if not input:
        input_dir = Path("input")
        if input_dir.exists():
            files = list(input_dir.glob("*.docx")) + list(input_dir.glob("*.md")) + list(input_dir.glob("*.html")) + list(input_dir.glob("*.txt"))
            if files:
                input = str(files[0])
            else:
                input = "examples/sample_article.md"
        else:
            input = "examples/sample_article.md"

    in_path = Path(input)
    console.print(Panel(f"[bold green]Human Writing Engine[/bold green]\nProcessing document: [yellow]{input}[/yellow]"))

    # 1. Ingestion
    console.print("[blue]Step 1/7:[/blue] Parsing document...")
    doc = parse_document(in_path)

    # 2. Outline / Baseline Alignment
    console.print("[blue]Step 2/7:[/blue] Aligning outline structure...")
    doc = generate_outline_document(doc)

    # 3. Generate 10 Variants via AI
    console.print("[blue]Step 3/7:[/blue] Generating 10 editorial persona variants via Vertex AI...")
    all_variants = asyncio.run(generate_10_variants(doc))

    # 4. Diversity Analysis (Filter Top 7 Retained Variants)
    console.print("[blue]Step 4/7:[/blue] Running diversity filter (discarding 3 most redundant, retaining top 7)...")
    retained_variants, div_report = filter_most_diverse_variants(all_variants, retain_count=7)
    console.print(f"  Retained personas (7 variants): {', '.join(div_report.retained_persona_ids)}")

    # Save all 7 retained variant DOCX files to output/variants/
    save_variant_documents(retained_variants, variants_dir, drafts_dir)
    console.print(f"  [bold cyan]Saved 7 retained variant DOCX files to:[/bold cyan] {variants_dir}")

    # 5. Local Deterministic Reconstruction (Read 7 variants section by section and merge - 0 LLM calls)
    console.print("[blue]Step 5/7:[/blue] Local Python reading 7 variants section-by-section and merging into brand-new 8th document (0 LLM calls)...")
    reconstructed_doc = reconstruct_article(retained_variants, doc)

    # 6. Style Refinement & Validation
    console.print("[blue]Step 6/7:[/blue] Applying style refinement and validating guardrails...")
    reconstructed_doc.raw_content = clean_ai_cliches(reconstructed_doc.raw_content)
    reconstructed_doc = optimize_document_readability(reconstructed_doc, target_body_words=doc.total_word_count)
    val_report = validate_article(reconstructed_doc, target_word_count=doc.total_word_count)

    # 7. Multi-Format Export of 8th Reconstructed Final Document
    console.print("[blue]Step 7/7:[/blue] Exporting final publication-ready outputs to final_doc/... ")
    stem = in_path.stem
    export_to_docx(reconstructed_doc, final_doc_dir / f"{stem}_humanized.docx", val_report)
    export_to_markdown(reconstructed_doc, final_doc_dir / f"{stem}_humanized.md", val_report)
    export_to_html(reconstructed_doc, final_doc_dir / f"{stem}_humanized.html", val_report)
    export_to_json(reconstructed_doc, final_doc_dir / f"{stem}_humanized.json", val_report)
    export_to_excel(reconstructed_doc, final_doc_dir / f"{stem}_quality_markers.xlsx", val_report, div_report, all_variants=all_variants)

    console.print(f"[bold green][OK] Done![/bold green]\nFinal 8th Document: [yellow]{final_doc_dir}[/yellow]\n7 Variant DOCX Files: [yellow]{variants_dir}[/yellow]")


@cli.command("process-brief")
@click.option("--brief", "-b", default=None, help="Content brief YAML file path (defaults to input/ folder)")
@click.option("--output-dir", "-o", default="./output", help="Output root directory")
def process_brief(brief: str, output_dir: str):
    """Generate a publication-ready article from a content brief (Mode B)."""
    out_root = Path(output_dir)
    final_doc_dir = out_root / "final_doc"
    variants_dir = out_root / "variants"
    drafts_dir = out_root / "drafts"

    final_doc_dir.mkdir(parents=True, exist_ok=True)
    variants_dir.mkdir(parents=True, exist_ok=True)
    drafts_dir.mkdir(parents=True, exist_ok=True)

    if not brief:
        input_dir = Path("input")
        if input_dir.exists():
            files = list(input_dir.glob("*.yaml")) + list(input_dir.glob("*.yml"))
            if files:
                brief = str(files[0])
            else:
                brief = "examples/sample_brief.yaml"
        else:
            brief = "examples/sample_brief.yaml"

    brief_path = Path(brief)
    console.print(Panel(f"[bold green]Human Writing Engine[/bold green]\nGenerating from brief: [yellow]{brief}[/yellow]"))

    with open(brief_path, "r", encoding="utf-8") as f:
        brief_data = yaml.safe_load(f)

    brief_model = ContentBriefModel(**brief_data)

    # 1. Plan baseline from brief
    console.print("[blue]Step 1/7:[/blue] Planning article outline from brief...")
    doc = prepare_plan_from_brief(brief_model)

    # 2. Outline refinement
    doc = generate_outline_document(doc)

    # 3. Generate 10 Variants via AI
    console.print("[blue]Step 3/7:[/blue] Generating 10 editorial persona variants via Vertex AI...")
    all_variants = asyncio.run(generate_10_variants(doc))

    # 4. Diversity Analysis (Filter Top 7 Retained Variants)
    console.print("[blue]Step 4/7:[/blue] Filtering top 7 most diverse variants...")
    retained_variants, div_report = filter_most_diverse_variants(all_variants, retain_count=7)

    save_variant_documents(retained_variants, variants_dir, drafts_dir)

    # 5. Local Reconstruction
    console.print("[blue]Step 5/7:[/blue] Local Python reading 7 variants section-by-section and merging into brand-new 8th document...")
    reconstructed_doc = reconstruct_article(retained_variants, doc)

    # 6. Style Refinement & Validation
    console.print("[blue]Step 6/7:[/blue] Cleaning clichés and validating editorial guardrails...")
    reconstructed_doc.raw_content = clean_ai_cliches(reconstructed_doc.raw_content)
    reconstructed_doc = optimize_document_readability(reconstructed_doc, target_body_words=brief_model.target_word_count)
    val_report = validate_article(reconstructed_doc, target_word_count=brief_model.target_word_count)

    # 7. Multi-Format Export
    console.print("[blue]Step 7/7:[/blue] Exporting final publication-ready outputs to final_doc/... ")
    stem = brief_path.stem
    export_to_docx(reconstructed_doc, final_doc_dir / f"{stem}_article.docx", val_report)
    export_to_markdown(reconstructed_doc, final_doc_dir / f"{stem}_article.md", val_report)
    export_to_html(reconstructed_doc, final_doc_dir / f"{stem}_article.html", val_report)
    export_to_json(reconstructed_doc, final_doc_dir / f"{stem}_article.json", val_report)
    export_to_excel(reconstructed_doc, final_doc_dir / f"{stem}_quality_markers.xlsx", val_report, div_report, all_variants=all_variants)

    console.print(f"[bold green][OK] Done![/bold green]\nFinal 8th Document: [yellow]{final_doc_dir}[/yellow]\n7 Variant DOCX Files: [yellow]{variants_dir}[/yellow]")


if __name__ == "__main__":
    cli()
