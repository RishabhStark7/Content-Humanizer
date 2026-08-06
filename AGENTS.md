# AGENTS.md

## Repository Instructions & Developer Guidelines

### Code Quality & Engineering Principles
1. **Language & Version**: Python 3.12+.
2. **Type Hints**: Mandatory for all function signatures and class definitions.
3. **Docstrings**: Google style docstrings for all classes and functions.
4. **LLM Boundary**: Google Vertex AI (Gemini) is strictly reserved for initial generation and brief planning. The **Human Reconstruction Engine (`src/reconstruction`) MUST run 100% locally in Python without any LLM API calls.**
5. **Validation Guardrails**: Outputs must pass all guardrail checks (word count bounds, FAQ min count & line length, heading hierarchy, Indian Grade 8 readability) before export.
