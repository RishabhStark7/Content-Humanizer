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
from src.ingestion.variant_parser import parse_user_input_variants
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
    """Save all retained variant documents as DOCX & Markdown files in output/variants/ and output/drafts/."""
    variants_dir.mkdir(parents=True, exist_ok=True)
    drafts_dir.mkdir(parents=True, exist_ok=True)

    for idx, v in enumerate(retained_variants, 1):
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
@click.option("--input", "-i", default=None, help="Input document path or input folder containing variant docs")
@click.option("--output-dir", "-o", default="./output", help="Output root directory")
def process_doc(input: str, output_dir: str):
    """Process an existing document or user-provided variant documents (0 AI calls if variants provided)."""
    out_root = Path(output_dir)
    final_doc_dir = out_root / "final_doc"
    variants_dir = out_root / "variants"
    drafts_dir = out_root / "drafts"

    final_doc_dir.mkdir(parents=True, exist_ok=True)
    variants_dir.mkdir(parents=True, exist_ok=True)
    drafts_dir.mkdir(parents=True, exist_ok=True)

    input_target = Path(input) if input else Path("input")

    # Check if input contains user-provided variants
    user_variants = []
    if input_target.is_dir():
        user_variants = parse_user_input_variants(input_target)
    elif input_target.is_file():
        user_variants = parse_user_input_variants(input_target)

    # MODE A: User provided multiple variants (or single multi-variant doc) in input/ -> 0 AI Calls!
    if len(user_variants) > 1:
        console.print(Panel(f"[bold green]Human Writing Engine (Local Variant Merger)[/bold green]\nDetected [yellow]{len(user_variants)} user-provided variants[/yellow] in input!"))
        console.print(f"[blue]Step 1/4:[/blue] Loaded {len(user_variants)} input variants. Skipping AI generation (0 LLM calls)...")

        save_variant_documents(user_variants, variants_dir, drafts_dir)

        console.print(f"[blue]Step 2/4:[/blue] Local Python reading {len(user_variants)} variants section-by-section and merging into brand-new blended document...")
        reconstructed_doc = reconstruct_article(user_variants)

        console.print("[blue]Step 3/4:[/blue] Applying style refinement and validating guardrails...")
        reconstructed_doc.raw_content = clean_ai_cliches(reconstructed_doc.raw_content)
        reconstructed_doc = optimize_document_readability(reconstructed_doc, target_body_words=user_variants[0].word_count)
        val_report = validate_article(reconstructed_doc, target_word_count=user_variants[0].word_count)

        console.print("[blue]Step 4/4:[/blue] Exporting final publication-ready outputs to final_doc/...")
        stem = user_variants[0].title.replace(" ", "_") if user_variants[0].title else "humanized_article"
        export_to_docx(reconstructed_doc, final_doc_dir / f"{stem}_humanized.docx", val_report)
        export_to_markdown(reconstructed_doc, final_doc_dir / f"{stem}_humanized.md", val_report)
        export_to_html(reconstructed_doc, final_doc_dir / f"{stem}_humanized.html", val_report)
        export_to_json(reconstructed_doc, final_doc_dir / f"{stem}_humanized.json", val_report)
        export_to_excel(reconstructed_doc, final_doc_dir / f"{stem}_quality_markers.xlsx", val_report, all_variants=user_variants)

        console.print(f"[bold green][OK] Done![/bold green]\nFinal Blended Document: [yellow]{final_doc_dir}[/yellow]\nInput Variants Saved: [yellow]{variants_dir}[/yellow]")
        return

    # MODE B: Single baseline document -> Generate 10 variants via Vertex AI and reconstruct locally
    in_path = input_target if input_target.is_file() else (list(Path("input").glob("*.docx")) + list(Path("input").glob("*.md")) + [Path("examples/sample_article.md")])[0]

    console.print(Panel(f"[bold green]Human Writing Engine[/bold green]\nProcessing single document: [yellow]{in_path}[/yellow]"))

    console.print("[blue]Step 1/7:[/blue] Parsing document...")
    doc = parse_document(in_path)

    console.print("[blue]Step 2/7:[/blue] Aligning outline structure...")
    doc = generate_outline_document(doc)

    console.print("[blue]Step 3/7:[/blue] Generating 10 editorial persona variants via Vertex AI...")
    all_variants = asyncio.run(generate_10_variants(doc))

    console.print("[blue]Step 4/7:[/blue] Running diversity filter (retaining top 7)...")
    retained_variants, div_report = filter_most_diverse_variants(all_variants, retain_count=7)

    save_variant_documents(retained_variants, variants_dir, drafts_dir)

    console.print("[blue]Step 5/7:[/blue] Local Python reading 7 variants section-by-section and merging into brand-new document (0 LLM calls)...")
    reconstructed_doc = reconstruct_article(retained_variants, doc)

    console.print("[blue]Step 6/7:[/blue] Applying style refinement and validating guardrails...")
    reconstructed_doc.raw_content = clean_ai_cliches(reconstructed_doc.raw_content)
    reconstructed_doc = optimize_document_readability(reconstructed_doc, target_body_words=doc.total_word_count)
    val_report = validate_article(reconstructed_doc, target_word_count=doc.total_word_count)

    console.print("[blue]Step 7/7:[/blue] Exporting final publication-ready outputs to final_doc/...")
    stem = in_path.stem
    export_to_docx(reconstructed_doc, final_doc_dir / f"{stem}_humanized.docx", val_report)
    export_to_markdown(reconstructed_doc, final_doc_dir / f"{stem}_humanized.md", val_report)
    export_to_html(reconstructed_doc, final_doc_dir / f"{stem}_humanized.html", val_report)
    export_to_json(reconstructed_doc, final_doc_dir / f"{stem}_humanized.json", val_report)
    export_to_excel(reconstructed_doc, final_doc_dir / f"{stem}_quality_markers.xlsx", val_report, div_report, all_variants=all_variants)

    console.print(f"[bold green][OK] Done![/bold green]\nFinal Document: [yellow]{final_doc_dir}[/yellow]\n7 Variant DOCX Files: [yellow]{variants_dir}[/yellow]")


@cli.command("process-brief")
@click.option("--brief", "-b", default=None, help="Content brief YAML file path")
@click.option("--output-dir", "-o", default="./output", help="Output root directory")
def process_brief(brief: str, output_dir: str):
    """Generate a publication-ready article from a content brief."""
    out_root = Path(output_dir)
    final_doc_dir = out_root / "final_doc"
    variants_dir = out_root / "variants"
    drafts_dir = out_root / "drafts"

    final_doc_dir.mkdir(parents=True, exist_ok=True)
    variants_dir.mkdir(parents=True, exist_ok=True)
    drafts_dir.mkdir(parents=True, exist_ok=True)

    if not brief:
        input_dir = Path("input")
        files = list(input_dir.glob("*.yaml")) + list(input_dir.glob("*.yml")) + [Path("examples/sample_brief.yaml")]
        brief = str(files[0])

    brief_path = Path(brief)
    console.print(Panel(f"[bold green]Human Writing Engine[/bold green]\nGenerating from brief: [yellow]{brief}[/yellow]"))

    with open(brief_path, "r", encoding="utf-8") as f:
        brief_data = yaml.safe_load(f)

    brief_model = ContentBriefModel(**brief_data)

    console.print("[blue]Step 1/7:[/blue] Planning article outline from brief...")
    doc = prepare_plan_from_brief(brief_model)

    doc = generate_outline_document(doc)

    console.print("[blue]Step 3/7:[/blue] Generating 10 editorial persona variants via Vertex AI...")
    all_variants = asyncio.run(generate_10_variants(doc))

    console.print("[blue]Step 4/7:[/blue] Filtering top 7 most diverse variants...")
    retained_variants, div_report = filter_most_diverse_variants(all_variants, retain_count=7)

    save_variant_documents(retained_variants, variants_dir, drafts_dir)

    console.print("[blue]Step 5/7:[/blue] Local Python reading 7 variants section-by-section and merging into brand-new document...")
    reconstructed_doc = reconstruct_article(retained_variants, doc)

    console.print("[blue]Step 6/7:[/blue] Cleaning clichés and validating editorial guardrails...")
    reconstructed_doc.raw_content = clean_ai_cliches(reconstructed_doc.raw_content)
    reconstructed_doc = optimize_document_readability(reconstructed_doc, target_body_words=brief_model.target_word_count)
    val_report = validate_article(reconstructed_doc, target_word_count=brief_model.target_word_count)

    console.print("[blue]Step 7/7:[/blue] Exporting final publication-ready outputs to final_doc/...")
    stem = brief_path.stem
    export_to_docx(reconstructed_doc, final_doc_dir / f"{stem}_article.docx", val_report)
    export_to_markdown(reconstructed_doc, final_doc_dir / f"{stem}_article.md", val_report)
    export_to_html(reconstructed_doc, final_doc_dir / f"{stem}_article.html", val_report)
    export_to_json(reconstructed_doc, final_doc_dir / f"{stem}_article.json", val_report)
    export_to_excel(reconstructed_doc, final_doc_dir / f"{stem}_quality_markers.xlsx", val_report, div_report, all_variants=all_variants)

    console.print(f"[bold green][OK] Done![/bold green]\nFinal Document: [yellow]{final_doc_dir}[/yellow]\n7 Variant DOCX Files: [yellow]{variants_dir}[/yellow]")


if __name__ == "__main__":
    cli()
