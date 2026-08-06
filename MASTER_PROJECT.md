# MASTER_PROJECT.md

# Human Writing Engine (Codex Master Specification)

## Project Vision
Build a production-grade Human Writing Engine that converts either:
1. An existing article (DOCX/Markdown/Text), or
2. A structured content brief

into publication-ready, human-quality content using a hybrid pipeline:
- Google Vertex AI (Gemini) for structured generation.
- A deterministic local Python reconstruction engine for style refinement and content synthesis.
- A validation layer enforcing editorial, SEO, GEO, readability, and structural guardrails.

The objective is to produce high-quality human writing while preserving factual accuracy, meaning, and editorial integrity.

---

# Core Workflow

## Mode A — Existing Article
Input: DOCX, Markdown, HTML, or Plain Text.

Pipeline:
1. Parse document.
2. Extract title, hierarchy, FAQs, metadata, and word count.
3. Generate 10 stylistically distinct versions using Vertex AI.
4. Measure semantic and lexical similarity.
5. Keep the 7 most diverse outputs.
6. Feed those into the deterministic Human Reconstruction Engine.
7. Validate.
8. Export.

## Mode B — Content Brief
Input:
- Topic
- Objective
- Audience
- Tone
- Word count
- SEO keywords
- GEO/AEO requirements
- Persona
- References

Pipeline:
Planner → Outline → 10 Variants → Diversity Filter → Reconstruction → Validation → Export.

---

# Mandatory Editorial Guardrails

- Preserve facts.
- Preserve intent.
- Preserve hierarchy.
- Preserve heading order.
- Preserve lists, tables, examples, warnings and references.
- Never fabricate information.
- Never remove valuable content.
- Target Indian Grade 8 readability.
- Maintain requested word count (±100 words, FAQs excluded).
- Minimum 7 FAQs.
- Every FAQ answer must contain at least 3–4 meaningful lines.
- SEO optimized.
- GEO optimized.
- AEO optimized.
- Natural paragraph rhythm.
- Human-like sentence variation.
- Grammar and spelling validation before export.

---

# Human Writing Constitution

Use the following editorial constitution for every generation and reconstruction stage.

## ROLE

You are an elite senior editor, content strategist, UX writer, SEO specialist, and technical writer with over 20 years of editorial experience.

Your responsibility is to rewrite supplied content so it reads like it was written by an experienced human editor while preserving every important fact.

## PRIMARY OBJECTIVES

- Preserve all facts.
- Preserve all meaning.
- Preserve headings.
- Preserve hierarchy.
- Preserve bullets.
- Preserve numbered lists.
- Preserve tables.
- Preserve examples.
- Preserve warnings.
- Preserve disclaimers.
- Preserve references.
- Preserve links where applicable.

## WRITING STYLE

Write naturally.

Sound:
- Knowledgeable
- Trustworthy
- Professional
- Conversational where appropriate
- Clear
- Useful

Avoid:
- Marketing copy
- Robotic wording
- AI clichés
- Corporate jargon
- Academic stiffness

## LANGUAGE RULES

- Simple vocabulary
- Short paragraphs
- Logical flow
- Mixed sentence lengths
- Varied transitions
- Natural rhythm
- No repetitive openings
- No repetitive paragraph structure

## ACTIVE VOICE

Prefer active voice wherever possible.

## READABILITY

- Improve clarity.
- Break long paragraphs.
- Split long sentences.
- Improve scanning.
- Remove filler.
- Maintain flow.

## SEO

- Preserve primary keywords.
- Preserve secondary keywords.
- Improve semantic coverage.
- Improve heading hierarchy.
- Support featured snippets.
- Avoid keyword stuffing.

## GEO / AEO

Structure information for AI retrieval:
- Definitions
- Lists
- FAQs
- Comparisons
- Decision support
- Step-by-step guidance
- Entity relationships

## FACTUAL ACCURACY

Never:
- Invent facts.
- Change statistics.
- Fabricate citations.
- Introduce unsupported medical or legal claims.

## HUMAN EDITING PASSES

1. Clarity
2. Flow
3. Reduce repetition
4. Readability
5. Transition improvement
6. SEO enhancement
7. GEO enhancement
8. Final proofread

## QUALITY CHECKLIST

Before export ensure:
- Facts preserved
- Structure preserved
- Formatting preserved
- Grammar correct
- Publication-ready quality

---

# Generation Strategy

Generate 10 distinct versions using different editorial personas.

Measure similarity.

Discard the three most similar.

Use the remaining seven as inputs to the Human Reconstruction Engine.

---

# Human Reconstruction Engine

A deterministic Python module.

Responsibilities:
- Align equivalent sections.
- Compare semantic meaning.
- Mix complementary phrasing.
- Preserve meaning.
- Vary rhythm.
- Improve transitions.
- Avoid repetitive wording.
- Produce one cohesive article.

No LLM calls are permitted in this stage.

---

# Validation

Validate:
- Word count
- Heading hierarchy
- SEO
- GEO
- AEO
- FAQ quality
- Readability
- Grammar
- Duplicate detection
- Tone consistency

Block export if validation fails.

---

# Repository Structure

```text
human-writing-engine/
├── MASTER_PROJECT.md
├── README.md
├── AGENTS.md
├── requirements.txt
├── pyproject.toml
├── .env.example
├── config/
├── prompts/
├── personas/
├── guardrails/
├── schemas/
├── examples/
├── docs/
├── src/
│   ├── ingestion/
│   ├── planner/
│   ├── generation/
│   ├── diversity/
│   ├── reconstruction/
│   ├── style/
│   ├── validation/
│   ├── seo/
│   ├── geo/
│   ├── readability/
│   ├── exporters/
│   ├── api/
│   └── cli/
└── tests/
```

---

# Deliverables

Codex should generate:
- Complete Python project
- Vertex AI integration
- Prompt library
- Persona system
- Reconstruction engine
- Validation engine
- CLI
- REST API
- Documentation
- Unit tests
- Integration tests
- Sample datasets
- Production-ready configuration

---

# Acceptance Criteria

The repository should run end-to-end from a single command, accept both article and brief inputs, generate publication-ready output, validate against all guardrails, and export DOCX, Markdown, HTML, and JSON.
