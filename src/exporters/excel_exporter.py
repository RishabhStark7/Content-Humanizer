"""Exporter for Excel summary report containing quality markers, validation status, and full 10 draft variants."""

from pathlib import Path
from typing import Union, List
import pandas as pd
from schemas.document import DocumentModel
from schemas.validation import ValidationReport
from schemas.diversity import DiversityReport
from schemas.variant import VariantOutput


def export_to_excel(
    document: DocumentModel,
    output_path: Union[str, Path],
    validation_report: ValidationReport = None,
    diversity_report: DiversityReport = None,
    all_variants: List[VariantOutput] = None
) -> Path:
    """Export executive editorial summary, quality markers, diversity report, and full 10 draft variants to Excel.

    Args:
        document: Synthesized DocumentModel.
        output_path: Target Excel file path (.xlsx).
        validation_report: Optional ValidationReport.
        diversity_report: Optional DiversityReport.
        all_variants: Optional List of 10 generated VariantOutput items.

    Returns:
        Path of saved .xlsx file.
    """
    out_file = Path(output_path)
    out_file.parent.mkdir(parents=True, exist_ok=True)

    # 1. Summary Sheet
    summary_data = {
        "Metric / Property": [
            "Document Title",
            "Original Format",
            "Total Word Count",
            "FAQ Count",
            "Section Count",
            "Overall Validation Passed",
            "Flesch Kincaid Grade",
            "Flesch Reading Ease"
        ],
        "Value": [
            document.title,
            document.original_format,
            document.total_word_count,
            len(document.faqs),
            len(document.sections),
            validation_report.passed if validation_report else "N/A",
            validation_report.metrics.get("flesch_kincaid_grade", 8.0) if validation_report else "N/A",
            validation_report.metrics.get("flesch_reading_ease", 65.0) if validation_report else "N/A"
        ]
    }
    df_summary = pd.DataFrame(summary_data)

    # 2. Validation Guardrail Markers Sheet
    if validation_report:
        markers_data = {
            "Guardrail Name": [
                validation_report.word_count_check.name,
                validation_report.readability_check.name,
                validation_report.faq_check.name,
                validation_report.heading_hierarchy_check.name,
                validation_report.seo_check.name,
                validation_report.geo_aeo_check.name,
                validation_report.cliche_check.name
            ],
            "Status": [
                "PASSED [✔]" if validation_report.word_count_check.passed else "FAILED [✘]",
                "PASSED [✔]" if validation_report.readability_check.passed else "FAILED [✘]",
                "PASSED [✔]" if validation_report.faq_check.passed else "FAILED [✘]",
                "PASSED [✔]" if validation_report.heading_hierarchy_check.passed else "FAILED [✘]",
                "PASSED [✔]" if validation_report.seo_check.passed else "FAILED [✘]",
                "PASSED [✔]" if validation_report.geo_aeo_check.passed else "FAILED [✘]",
                "PASSED [✔]" if validation_report.cliche_check.passed else "FAILED [✘]"
            ],
            "Score": [
                validation_report.word_count_check.score,
                validation_report.readability_check.score,
                validation_report.faq_check.score,
                validation_report.heading_hierarchy_check.score,
                validation_report.seo_check.score,
                validation_report.geo_aeo_check.score,
                validation_report.cliche_check.score
            ],
            "Details & Findings": [
                validation_report.word_count_check.details,
                validation_report.readability_check.details,
                validation_report.faq_check.details,
                validation_report.heading_hierarchy_check.details,
                validation_report.seo_check.details,
                validation_report.geo_aeo_check.details,
                validation_report.cliche_check.details
            ]
        }
        df_markers = pd.DataFrame(markers_data)
    else:
        df_markers = pd.DataFrame({"Guardrail Name": [], "Status": [], "Score": [], "Details & Findings": []})

    # 3. Diversity Analysis Sheet
    if diversity_report:
        div_data = {
            "Category": [
                "Total Variants Generated",
                "Retained Variants Count",
                "Discarded Variants Count",
                "Retained Persona List",
                "Discarded Persona List"
            ],
            "Details": [
                diversity_report.total_generated,
                diversity_report.retained_count,
                diversity_report.discarded_count,
                ", ".join(diversity_report.retained_persona_ids),
                ", ".join(diversity_report.discarded_persona_ids)
            ]
        }
        df_diversity = pd.DataFrame(div_data)
    else:
        df_diversity = pd.DataFrame({"Category": [], "Details": []})

    # 4. 10 Draft Variants Sheet
    if all_variants:
        drafts_data = {
            "Persona ID": [v.persona_id for v in all_variants],
            "Persona Name": [v.persona_name for v in all_variants],
            "Word Count": [v.word_count for v in all_variants],
            "Status": [
                "Retained" if (diversity_report and v.persona_id in diversity_report.retained_persona_ids) else "Discarded"
                for v in all_variants
            ],
            "Draft Content Preview": [v.raw_text[:500] + "..." if len(v.raw_text) > 500 else v.raw_text for v in all_variants],
            "Full Draft Markdown Content": [v.raw_text for v in all_variants]
        }
        df_drafts = pd.DataFrame(drafts_data)
    else:
        df_drafts = pd.DataFrame({"Persona ID": [], "Persona Name": [], "Word Count": [], "Status": [], "Full Draft Markdown Content": []})

    # Write multi-sheet Excel file using pandas + openpyxl
    try:
        with pd.ExcelWriter(str(out_file), engine="openpyxl") as writer:
            df_summary.to_excel(writer, sheet_name="Executive Summary", index=False)
            df_markers.to_excel(writer, sheet_name="Quality Guardrail Markers", index=False)
            df_diversity.to_excel(writer, sheet_name="Diversity Analysis", index=False)
            df_drafts.to_excel(writer, sheet_name="10 Draft Variants", index=False)
    except PermissionError:
        alt_file = out_file.parent / f"{out_file.stem}_new.xlsx"
        with pd.ExcelWriter(str(alt_file), engine="openpyxl") as writer:
            df_summary.to_excel(writer, sheet_name="Executive Summary", index=False)
            df_markers.to_excel(writer, sheet_name="Quality Guardrail Markers", index=False)
            df_diversity.to_excel(writer, sheet_name="Diversity Analysis", index=False)
            df_drafts.to_excel(writer, sheet_name="10 Draft Variants", index=False)
        return alt_file

    return out_file
