# 📄 AI Resume Reviewer

> AI-powered ATS resume analyzer built with **Streamlit**, **IBM watsonx.ai**, and **IBM Docling**.

Upload a PDF resume, paste a job description, and get an instant structured analysis — ATS score, keyword gaps, section scores, strengths/weaknesses, and actionable improvement suggestions.

---

## 🚀 Quick Start (Local)

```bash
# 1. Clone
git clone https://github.com/plottwist3017/ai-resume-reviewer
cd ai-resume-reviewer

# 2. Virtual environment
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS/Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Add credentials
cp .env.example .env
# Edit .env with your IBM Cloud API key and watsonx.ai Project ID

# 5. Run
streamlit run app.py
```

---

## 🔑 Credentials

### Running locally — `.env` file

Copy `.env.example` to `.env` and fill in your values:

```env
WATSONX_API_KEY=your_ibm_cloud_api_key
WATSONX_PROJECT_ID=your_watsonx_project_id
WATSONX_URL=https://ca-tor.ml.cloud.ibm.com
WATSONX_MODEL_ID=meta-llama/llama-3-3-70b-instruct
```

### Deployed on Streamlit Community Cloud — Secrets

Go to your app on **share.streamlit.io → ⋮ → Settings → Secrets** and paste:

```toml
WATSONX_API_KEY = "your_ibm_cloud_api_key"
WATSONX_PROJECT_ID = "your_watsonx_project_id"
WATSONX_URL = "https://ca-tor.ml.cloud.ibm.com"
WATSONX_MODEL_ID = "meta-llama/llama-3-3-70b-instruct"
```

> ⚠️ Never commit your real `.env` file. It is listed in `.gitignore`.

---

## ✨ Features

| Feature | Details |
|---|---|
| **PDF Extraction** | IBM Docling converts any text-based PDF to clean markdown-level text |
| **AI Analysis** | IBM watsonx.ai (Llama / Granite) returns a structured JSON evaluation |
| **ATS Scoring** | Overall Score, ATS Score, Skills Match % |
| **Keyword Gap** | Missing keywords identified from the job description |
| **Section Scores** | Summary, Experience, Education, Skills, Formatting, Keywords |
| **Visualisations** | Gauge charts, radar chart, bar chart, donut chart (Plotly) |
| **Extracted Info** | Technical skills, soft skills, experience, education, certifications, projects |
| **Recommendations** | Strengths, weaknesses, grammar tips, improvement list |
| **Final Verdict** | Strong / Moderate / Weak Match with rationale |
| **Export** | Download as PDF report, CSV spreadsheet, or raw JSON |

---

## 📦 Dependencies

| Package | Purpose |
|---|---|
| `streamlit` | Web UI |
| `docling` | IBM PDF-to-text extraction |
| `requests` | watsonx.ai REST API calls |
| `python-dotenv` | `.env` credential loading |
| `pandas` | CSV export |
| `plotly` | Interactive charts |
| `fpdf2` | PDF report generation |

---

## 🗂 Project Structure

```
ai-resume-reviewer/
├── app.py               # Main Streamlit application
├── requirements.txt     # Python dependencies
├── .env.example         # Credential template (copy to .env)
├── .streamlit/
│   └── config.toml      # Streamlit server config
└── README.md
```

---

## ⚠️ Notes

- Resume text is **not stored** — all processing is in-memory per session.
- For scanned (image-based) PDFs, set `do_ocr=True` in `extract_text_docling()` to enable OCR.
- AI feedback is guidance only — always review suggestions critically.

---

*MIT License — free to use, modify, and distribute.*
