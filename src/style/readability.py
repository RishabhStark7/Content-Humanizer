"""Readability scoring and Grade 8 optimization engine for natural human prose flow."""

import re
import textstat
from schemas.document import DocumentModel

SIMPLE_VOCABULARY_MAP = {
    "pharmaceutical": "drug",
    "pharmaceuticals": "drugs",
    "hospitalization": "hospital stay",
    "hospitalizations": "hospital stays",
    "interventions": "actions",
    "intervention": "action",
    "manifest": "show",
    "manifestation": "sign",
    "utilization": "use",
    "substantiate": "prove",
    "substantiated": "proven",
    "complications": "problems",
    "complication": "problem",
    "practitioners": "doctors",
    "practitioner": "doctor",
    "administration": "care",
    "subsequently": "later",
    "consequently": "so",
    "additionally": "also",
    "recommendations": "advice",
    "implementation": "setup",
    "specifications": "details",
    "significantly": "greatly",
    "proactive": "early",
    "hypertension": "high blood pressure",
    "cardiovascular": "heart",
    "immunizations": "shots",
    "immunization": "shot",
    "paramount": "vital",
    "traceability": "tracking",
    "accountability": "duty",
    "fulfilment": "delivery",
    "transportation": "transit",
    "expectations": "standards",
    "unsuitable": "unfit",
    "authorities": "officials",
    "identification": "finding",
    "documentation": "records",
    "assessments": "checks",
    "assessment": "check",
    "examination": "check",
    "examinations": "checks",
    "technological": "tech",
    "inventory": "stock",
    "approaching": "near",
    "responsibility": "duty",
    "management": "care",
    "consideration": "thought",
    "guidance": "advice",
    "regulations": "laws",
    "accordance": "agreement",
    "authorized": "approved",
    "processes": "steps",
    "process": "step",
    "requirements": "rules",
    "requirement": "rule",
    "considerations": "factors",
    "medications": "drugs",
    "medication": "drug",
    "precautions": "steps",
    "precaution": "step",
}


def clean_text_for_readability(text: str) -> str:
    """Remove markdown heading hashes and structural symbols for accurate textstat calculation."""
    lines = text.splitlines()
    prose_lines = []
    for l in lines:
        stripped = l.strip()
        if stripped.startswith("#"):
            cleaned_heading = re.sub(r"^#+\s*", "", stripped)
            if not cleaned_heading.endswith((".", "!", "?")):
                cleaned_heading += "."
            prose_lines.append(cleaned_heading)
        else:
            prose_lines.append(stripped)
    return " ".join(prose_lines)


def calculate_flesch_reading_ease(text: str) -> float:
    """Calculate Flesch Reading Ease score (higher is easier to read, target >= 40+)."""
    if not text.strip():
        return 70.0
    clean_prose = clean_text_for_readability(text)
    try:
        score = textstat.flesch_reading_ease(clean_prose)
        return float(score)
    except Exception:
        return 65.0


def calculate_flesch_kincaid_grade(text: str) -> float:
    """Calculate Flesch Kincaid Grade level (target Indian Grade 8 = ~7.5-8.5)."""
    if not text.strip():
        return 8.0
    clean_prose = clean_text_for_readability(text)
    try:
        grade = textstat.flesch_kincaid_grade(clean_prose)
        return float(grade) if grade > 0 else 8.0
    except Exception:
        return 8.0


def optimize_for_grade_8_readability(text: str) -> str:
    """Transform text to natural human editorial prose while optimizing vocabulary for Grade 8 readability.

    NO artificial word chunking is performed. Sentences are kept grammatically complete.
    """
    if not text.strip():
        return text

    # 1. Clean punctuation artifacts & mock phrases
    cleaned = text.replace(":.", ".").replace("?.", "?").replace("!.", "!").replace("..", ".").replace(" ,", ",")
    cleaned = re.sub(r"\s*([.,!?])", r"\1", cleaned)  # Fix space before punctuation
    cleaned = re.sub(r"([.,!?])([A-Za-z])", r"\1 \2", cleaned)  # Ensure space after punctuation

    mock_phrases = [
        r"Here is what you need to know:\s*",
        r"It is simpler than it looks once you get the hang of it\.\s*",
        r"In today's fast-moving environment,\s*",
        r"The strategic takeaway is undeniably compelling\.\s*",
        r"Considering contemporary reader demand and real-time context,\s*",
        r"Addressing these timely requirements ensures peak relevance today\.\s*",
        r"Empirical data confirms that\s*"
    ]
    for mp in mock_phrases:
        cleaned = re.sub(mp, "", cleaned, flags=re.IGNORECASE)

    # 2. Substitute multi-syllable academic vocabulary with natural simple words
    for complex_word, simple_word in SIMPLE_VOCABULARY_MAP.items():
        pattern = re.compile(rf"\b{complex_word}\b", re.IGNORECASE)
        cleaned = pattern.sub(simple_word, cleaned)

    # 3. Clean up sentence flow naturally and remove consecutive duplicate sentences
    lines = cleaned.split("\n")
    processed_lines = []

    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            processed_lines.append(line)
            continue

        raw_sentences = re.split(r"(?<=[.!?])\s+", stripped)
        clean_sentences = []

        for s in raw_sentences:
            s_clean = s.strip()
            if not s_clean:
                continue

            # Ensure sentence starts with capital letter and ends with punctuation
            if s_clean[0].islower():
                s_clean = s_clean[0].upper() + s_clean[1:]
            if not s_clean.endswith((".", "!", "?")):
                s_clean += "."

            # Remove exact consecutive duplicates
            if not clean_sentences or clean_sentences[-1].lower() != s_clean.lower():
                clean_sentences.append(s_clean)

        processed_lines.append(" ".join(clean_sentences))

    return "\n".join(processed_lines)


def optimize_document_readability(document: DocumentModel, target_body_words: int = 1200) -> DocumentModel:
    """Optimize DocumentModel sections and raw_content for natural human reading flow."""
    for sec in document.sections:
        sec.content = optimize_for_grade_8_readability(sec.content)
        sec.word_count = len(sec.content.split())

    full_parts = []
    for sec in document.sections:
        full_parts.append(f"## {sec.heading}\n{sec.content}")
        if sec.bullets:
            full_parts.append("\n".join(f"- {b}" for b in sec.bullets))

    if document.faqs:
        full_parts.append("## Frequently Asked Questions (FAQs)")
        for f in document.faqs:
            f.answer = optimize_for_grade_8_readability(f.answer)
            f.word_count = len(f.answer.split())
            full_parts.append(f"### {f.question}\n{f.answer}")

    document.raw_content = "\n\n".join(full_parts)
    document.total_word_count = len(document.raw_content.split())
    return document
