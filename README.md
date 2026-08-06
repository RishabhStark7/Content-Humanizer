# Human Writing Engine

> Production-grade editorial pipeline for long-form content generation, diversity filtering, deterministic local reconstruction, and automated editorial validation.

## Overview

The **Human Writing Engine** synthesizes publication-ready articles from existing documents (DOCX, Markdown, HTML, Plain text) or structured content briefs. By generating 10 distinct editorial variants via Google Vertex AI (Gemini), selecting the 7 most diverse versions, and reconstructing them into a single cohesive article using a local deterministic Python engine, it avoids formulaic AI patterns and delivers high-quality writing adhering to strict editorial standards.

## Architectural Pipeline

```text
Input (Doc / Brief) → Ingestion Parser → Content Planner → Vertex AI Generation (10 Personas)
  ↓
Diversity Analysis (Keeps 7 Most Diverse) → Human Reconstruction Engine (Pure Python)
  ↓
Style Refinement → Validation Guardrails → Multi-Format Export (DOCX, Markdown, HTML, JSON)
```

## Quick Start

### 1. Installation
```bash
pip install -r requirements.txt
pip install -e .
```

### 2. Environment Setup
Copy `.env.example` to `.env` and fill in your Vertex AI credentials:
```bash
cp .env.example .env
```

### 3. Command Line Interface (CLI)

#### Process an Existing Document (Mode A):
```bash
python -m src.cli.main process-doc --input examples/sample_article.md --output-dir ./dist
```

#### Generate from a Content Brief (Mode B):
```bash
python -m src.cli.main process-brief --brief examples/sample_brief.yaml --output-dir ./dist
```

### 4. REST API
Start the FastAPI server:
```bash
python -m src.api.app
```
Access interactive documentation at `http://localhost:8000/docs`.

## Running Tests
```bash
pytest -v tests/
```
