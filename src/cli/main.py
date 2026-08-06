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


def save_draft_variants(variants, reconstructed_doc, drafts_dir: Path):
    """Save Version 1 (Educational), Version 2 (Conversational), Version 3 (Patient-first), and Version 4 (Reconstructed Blended) for full visibility."""
    drafts_dir.mkdir(parents=True, exist_ok=True)

    # Map primary versions
    v1_educational = next((v for v in variants if "technical" in v.persona_id or "scientific" in v.persona_id or "senior" in v.persona_id), variants[0] if variants else None)
    v2_conversational = next((v for v in variants if "conversational" in v.persona_id or "educator" in v.persona_id), variants[1] if len(variants) > 1 else None)
    v3_patient_first = next((v for v in variants if "story" in v.persona_id or "demand" in v.persona_id or "evidence" in v.persona_id), variants[2] if len(variants) > 2 else None)

    if v1_educational:
        (drafts_dir / "Version_1_Educational.md").write_text(f"---\nversion: \"Version 1\"\nstyle: \"Educational (Clear, Structured, Neutral)\"\npersona: \"{v1_educational.persona_name}\"\n---\n\n" + v1_educational.raw_text, encoding="utf-8")

    if v2_conversational:
        (drafts_dir / "Version_2_Conversational.md").write_text(f"---\nversion: \"Version 2\"\nstyle: \"Conversational (Natural, Patient-friendly, Warmer)\"\npersona: \"{v2_conversational.persona_name}\"\n---\n\n" + v2_conversational.raw_text, encoding="utf-8")

    if v3_patient_first:
        (drafts_dir / "Version_3_Patient_First.md").write_text(f"---\nversion: \"Version 3\"\nstyle: \"Patient-first (Relatable, Natural Rhythm)\"\npersona: \"{v3_patient_first.persona_name}\"\n---\n\n" + v3_patient_first.raw_text, encoding="utf-8")

    if reconstructed_doc:
        (drafts_dir / "Version_4_Reconstructed_Blended_Final.md").write_text(f"---\nversion: \"Version 4\"\nstyle: \"Reconstructed Blended Final (Pure Python Synthesis, 0 LLM Calls)\"\n---\n\n" + reconstructed_doc.raw_content, encoding="utf-8")

    # Also save individual persona variants 01-10
    for idx, v in enumerate(variants, 1):
        filename = f"{idx:02d}_{v.persona_id}.md"
        draft_path = drafts_dir / filename
        content = f"---\npersona_id: \"{v.persona_id}\"\npersona_name: \"{v.persona_name}\"\nword_count: {v.word_count}\n---\n\n" + v.raw_text
        draft_path.write_text(content, encoding="utf-8")


@cli.command("process-doc")
@click.option("--input", "-i", default=None, help="Input document path (defaults to auto-scanning input/ folder)")
@click.option("--output-dir", "-o", default="./output", help="Output root directory")
def process_doc(input: str, output_dir: str):
    """Process an existing document through the editorial pipeline (Mode A)."""
    out_root = Path(output_dir)
    final_doc_dir = out_root / "final_doc"
    drafts_dir = out_root / "drafts"

    final_doc_dir.mkdir(parents=True, exist_ok=True)
    drafts_dir.mkdir(parents=True, exist_ok=True)

    # If no input provided, auto-scan input/ folder
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

    # 3. Generate Variants (Version 1 Educational, Version 2 Conversational, Version 3 Patient-first)
    console.print("[blue]Step 3/7:[/blue] Generating Version 1 (Educational), Version 2 (Conversational), and Version 3 (Patient-first) variants via Vertex AI...")
    variants = asyncio.run(generate_10_variants(doc))

    # 4. Diversity Analysis (Keep 7, Discard 3)
    console.print("[blue]Step 4/7:[/blue] Running diversity filter (discarding 3 most redundant)...")
    retained_variants, div_report = filter_most_diverse_variants(variants, retain_count=7)
    console.print(f"  Retained personas: {', '.join(div_report.retained_persona_ids)}")
    console.print(f"  Discarded personas: {', '.join(div_report.discarded_persona_ids)}")

    # 5. Local Deterministic Reconstruction (Version 4 Blended - Pure Python, 0 LLM calls)
    console.print("[blue]Step 5/7:[/blue] Reconstructing Version 4 (Blended Final) with Local Human Reconstruction Engine (0 LLM calls)...")
    reconstructed_doc = reconstruct_article(retained_variants, doc)

    # 6. Style Refinement & Validation
    console.print("[blue]Step 6/7:[/blue] Applying style refinement and validating guardrails...")
    reconstructed_doc.raw_content = clean_ai_cliches(reconstructed_doc.raw_content)
    reconstructed_doc = optimize_document_readability(reconstructed_doc, target_body_words=doc.total_word_count)
    val_report = validate_article(reconstructed_doc, target_word_count=doc.total_word_count)

    # Save all draft versions (V1, V2, V3, V4) to output/drafts/ for full visibility
    save_draft_variants(variants, reconstructed_doc, drafts_dir)
    console.print(f"  [bold cyan]Saved Version 1, Version 2, Version 3, and Version 4 drafts to:[/bold cyan] {drafts_dir}")

    # 7. Multi-Format Export to output/final_doc/
    console.print("[blue]Step 7/7:[/blue] Exporting final publication-ready outputs to final_doc/...")
    stem = in_path.stem
    export_to_docx(reconstructed_doc, final_doc_dir / f"{stem}_humanized.docx", val_report)
    export_to_markdown(reconstructed_doc, final_doc_dir / f"{stem}_humanized.md", val_report)
    export_to_html(reconstructed_doc, final_doc_dir / f"{stem}_humanized.html", val_report)
    export_to_json(reconstructed_doc, final_doc_dir / f"{stem}_humanized.json", val_report)
    export_to_excel(reconstructed_doc, final_doc_dir / f"{stem}_quality_markers.xlsx", val_report, div_report, all_variants=variants)

    console.print(f"[bold green][OK] Done![/bold green]\nFinal Document: [yellow]{final_doc_dir}[/yellow]\nDrafts: [yellow]{drafts_dir}[/yellow]")


@cli.command("process-brief")
@click.option("--brief", "-b", default=None, help="Content brief YAML file path (defaults to input/ folder)")
@click.option("--output-dir", "-o", default="./output", help="Output root directory")
def process_brief(brief: str, output_dir: str):
    """Generate a publication-ready article from a content brief (Mode B)."""
    out_root = Path(output_dir)
    final_doc_dir = out_root / "final_doc"
    drafts_dir = out_root / "drafts"

    final_doc_dir.mkdir(parents=True, exist_ok=True)
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

    # 3. Generate Variants
    console.print("[blue]Step 3/7:[/blue] Generating Version 1 (Educational), Version 2 (Conversational), and Version 3 (Patient-first) variants via Vertex AI...")
    variants = asyncio.run(generate_10_variants(doc))

    # 4. Diversity Analysis
    console.print("[blue]Step 4/7:[/blue] Filtering top 7 most diverse variants...")
    retained_variants, div_report = filter_most_diverse_variants(variants, retain_count=7)

    # 5. Local Reconstruction
    console.print("[blue]Step 5/7:[/blue] Synthesizing Version 4 (Blended Final) via Human Reconstruction Engine...")
    reconstructed_doc = reconstruct_article(retained_variants, doc)

    # 6. Style Refinement & Validation
    console.print("[blue]Step 6/7:[/blue] Cleaning clichés and validating editorial guardrails...")
    reconstructed_doc.raw_content = clean_ai_cliches(reconstructed_doc.raw_content)
    reconstructed_doc = optimize_document_readability(reconstructed_doc, target_body_words=brief_model.target_word_count)
    val_report = validate_article(reconstructed_doc, target_word_count=brief_model.target_word_count)

    save_draft_variants(variants, reconstructed_doc, drafts_dir)
    console.print(f"  [bold cyan]Saved Version 1, Version 2, Version 3, and Version 4 drafts to:[/bold cyan] {drafts_dir}")

    # 7. Multi-Format Export
    console.print("[blue]Step 7/7:[/blue] Exporting publication-ready outputs to final_doc/...")
    stem = brief_path.stem
    export_to_docx(reconstructed_doc, final_doc_dir / f"{stem}_article.docx", val_report)
    export_to_markdown(reconstructed_doc, final_doc_dir / f"{stem}_article.md", val_report)
    export_to_html(reconstructed_doc, final_doc_dir / f"{stem}_article.html", val_report)
    export_to_json(reconstructed_doc, final_doc_dir / f"{stem}_article.json", val_report)
    export_to_excel(reconstructed_doc, final_doc_dir / f"{stem}_quality_markers.xlsx", val_report, div_report, all_variants=variants)

    console.print(f"[bold green][OK] Done![/bold green]\nFinal Document: [yellow]{final_doc_dir}[/yellow]\nDrafts: [yellow]{drafts_dir}[/yellow]")


if __name__ == "__main__":
    cli()
