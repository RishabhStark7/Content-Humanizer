# Human Writing Engine - VS Code Local Setup & Google Vertex AI Login Guide

This guide provides step-by-step instructions for running the **Human Writing Engine** locally in VS Code (without Antigravity), authenticating with Google Cloud Vertex AI, and processing documents to generate converted articles and Excel quality marker reports.

---

## 🛠️ Step 1: Prerequisites & VS Code Setup

### 1. Open Project in VS Code
1. Open VS Code.
2. Select **File > Open Folder...** and navigate to your project folder:
   ```text
   E:\Content_Humaniser
   ```
3. Open a new terminal in VS Code by pressing `Ctrl + ~` (or **Terminal > New Terminal**).

### 2. Verify Python 3.12+ Installation
Ensure Python 3.12+ is available:
```bash
python --version
```

### 3. Create & Activate Virtual Environment (Recommended)
```bash
# Create virtual environment
python -m venv .venv

# Activate on Windows PowerShell:
.\.venv\Scripts\Activate.ps1

# Or activate on Windows Command Prompt (cmd):
.\.venv\Scripts\activate.bat
```

### 4. Install Dependencies
Install all required Python packages:
```bash
pip install -r requirements.txt
pip install -e .
```

---

## 🔑 Step 2: Google Cloud & Vertex AI Authentication Login

To connect the engine to Google Vertex AI (Gemini) for live multi-persona generation:

### Option A: Using Google Cloud SDK (gcloud CLI) - Recommended

1. **Install Google Cloud CLI** (if not already installed):
   Download and install from [cloud.google.com/sdk/docs/install](https://cloud.google.com/sdk/docs/install).

2. **Login to Google Cloud**:
   Run the login command in VS Code terminal:
   ```bash
   gcloud auth login
   ```
   *A browser window will open. Log in with your Google account that has access to Vertex AI.*

3. **Authenticate Application Default Credentials (ADC)**:
   This allows Python scripts to access Vertex AI automatically:
   ```bash
   gcloud auth application-default login
   ```

4. **Set Your Google Cloud Project**:
   ```bash
   gcloud config set project YOUR_GOOGLE_CLOUD_PROJECT_ID
   ```

---

### Option B: Using Service Account Key JSON

1. Download your Service Account JSON Key file from Google Cloud Console (**IAM & Admin > Service Accounts > Keys**).
2. Save the key JSON file in your project folder (e.g. `gcp-key.json`).
3. Set the environment variable in VS Code terminal:

   **PowerShell:**
   ```powershell
   $env:GOOGLE_APPLICATION_CREDENTIALS="E:\Content_Humaniser\gcp-key.json"
   $env:GOOGLE_CLOUD_PROJECT="YOUR_GOOGLE_CLOUD_PROJECT_ID"
   $env:MOCK_VERTEX_AI="False"
   ```

   **CMD:**
   ```cmd
   set GOOGLE_APPLICATION_CREDENTIALS=E:\Content_Humaniser\gcp-key.json
   set GOOGLE_CLOUD_PROJECT=YOUR_GOOGLE_CLOUD_PROJECT_ID
   set MOCK_VERTEX_AI=False
   ```

---

## ⚙️ Step 3: Configure Environment Variables (`.env`)

Copy `.env.example` to `.env`:
```bash
copy .env.example .env
```

Edit your `.env` file with your credentials and settings:
```ini
# Google Cloud & Vertex AI Settings
GOOGLE_CLOUD_PROJECT=YOUR_GOOGLE_CLOUD_PROJECT_ID
VERTEX_LOCATION=us-central1
GOOGLE_APPLICATION_CREDENTIALS=gcp-key.json

# Set MOCK_VERTEX_AI=False to use live Vertex AI Gemini API
# Set MOCK_VERTEX_AI=True for local testing without API credits
MOCK_VERTEX_AI=False
```

---

## 🚀 Step 4: Running the Engine Locally

### Mode A: Process an Existing Document (DOCX / MD / HTML / Text)

To run the pipeline on your document `What Happens to Expired or Rejected Medicines.docx`:

```bash
python -m src.cli.main process-doc --input "What Happens to Expired or Rejected Medicines.docx" --output-dir ./output
```

---

### Mode B: Generate from a Content Brief

To generate a long-form article from a brief YAML file:

```bash
python -m src.cli.main process-brief --brief examples/sample_brief.yaml --output-dir ./output
```

---

## 📂 Step 5: Output Folder & Excel Markers Report

When execution completes, all generated documents and reports are automatically stored in the **`./output/`** folder:

```text
output/
├── What Happens to Expired or Rejected Medicines_humanized.docx   # Publication-ready DOCX
├── What Happens to Expired or Rejected Medicines_humanized.md     # Clean Markdown with frontmatter
├── What Happens to Expired or Rejected Medicines_humanized.html   # Styled Semantic HTML5
├── What Happens to Expired or Rejected Medicines_humanized.json   # Structured JSON payload
└── What Happens to Expired or Rejected Medicines_quality_markers.xlsx # Excel Report with Markers
```

### 📊 Excel Quality Markers Report (`.xlsx`)
The generated Excel file contains 3 detailed tabs:
1. **Executive Summary**: Title, total word count, FAQ count, section count, readability grade score.
2. **Quality Guardrail Markers**: Pass/Fail status (`PASSED [✔]` / `FAILED [✘]`), numerical score, and detailed findings for:
   - Word Count Guardrail (±100 words)
   - Readability Guardrail (Indian Grade 8 standard)
   - FAQ Guardrail (Minimum 7 FAQs, 3–4 lines per answer)
   - Heading Hierarchy Guardrail (H1 -> H2 -> H3)
   - SEO Guardrail
   - GEO / AEO Guardrail
   - AI Cliché Guardrail
3. **Diversity Analysis**: Summary of 10 persona variants generated, 7 retained personas, 3 discarded redundant personas, and mutual similarity scores.

---

## 🌐 Step 6: (Optional) Running the REST API Server

If you want to run the FastAPI REST server in VS Code:

```bash
python -m src.api.app
```
Access interactive API documentation in your browser at:
`http://localhost:8000/docs`
