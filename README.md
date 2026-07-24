# 📄 AI Resume Reviewer

> AI-powered ATS resume analyzer built with **Streamlit**, **IBM watsonx.ai**, and **IBM Docling**.

## 🎥 Demo

<p align="center">
  <img src="assets/demo.gif" width="900" alt="Application Demo">
</p>

Or watch the full demo:

https://github.com/yourusername/ai-resume-reviewer/assets/...

---

## 🚀 What it does

Upload a resume (PDF) and compare it against a job description to receive an instant AI-powered ATS review including:

- 📊 ATS Compatibility Score
- 🎯 Skills Match Percentage
- 🔍 Missing Keywords Detection
- 📑 Section-by-Section Resume Analysis
- 📈 Interactive Dashboard & Charts
- 💡 Personalized Improvement Suggestions
- 📄 Export to PDF, CSV, or JSON

---

## 🖼 Preview

*(Optional screenshots here)*

| Dashboard | Analysis |
|-----------|----------|
| screenshot | screenshot |

---

## 🛠 Tech Stack

- **Frontend:** Streamlit
- **AI:** IBM watsonx.ai (Granite / Llama)
- **Document Parsing:** IBM Docling
- **Visualization:** Plotly
- **Reports:** FPDF2
- **Data:** Pandas

---

## ⚡ Features

| Feature | Description |
|----------|-------------|
| PDF Extraction | IBM Docling converts resumes into structured text |
| AI Analysis | watsonx.ai evaluates resume against a JD |
| ATS Score | Overall ATS compatibility score |
| Keyword Gap | Finds missing keywords |
| Skill Match | Technical & soft skills comparison |
| Dashboard | Gauge, radar, donut & bar charts |
| Export | PDF, CSV & JSON |

---

## 📂 Project Structure

```text
ai-resume-reviewer/
│
├── app.py
├── requirements.txt
├── .env.example
├── assets/
│   ├── demo.gif
│   ├── dashboard.png
│   └── analysis.png
└── README.md
```

---

## 🚀 Installation

```bash
git clone https://github.com/yourusername/ai-resume-reviewer.git

cd ai-resume-reviewer

python -m venv .venv
```

Windows

```bash
.venv\Scripts\activate
```

Mac/Linux

```bash
source .venv/bin/activate
```

Install dependencies

```bash
pip install -r requirements.txt
```

Create `.env`

```env
WATSONX_API_KEY=...
WATSONX_PROJECT_ID=...
WATSONX_URL=https://us-south.ml.cloud.ibm.com
WATSONX_MODEL_ID=ibm/granite-13b-instruct-v2
```

Run

```bash
streamlit run app.py
```

---

## 🔑 IBM watsonx.ai Setup

1. Create an IBM Cloud account.
2. Provision the **watsonx.ai** service.
3. Create a Project.
4. Copy the Project ID.
5. Generate an API Key.

---

## 🧠 AI Workflow

```text
Resume PDF
      │
      ▼
 IBM Docling
      │
      ▼
 Extracted Text
      │
      ▼
Job Description
      │
      ▼
IBM watsonx.ai
      │
      ▼
Structured JSON Analysis
      │
      ▼
Dashboard + Reports
```

---

## 📦 Export Formats

- PDF Report
- CSV Summary
- JSON Output

---

assets/
├── demo.gif
├── dashboard.png
├── upload.png
├── report.png
└── workflow.png

---

## ⚠️ Notes

- No resume data is stored.
- Processing is session-only.
- OCR can be enabled for scanned PDFs.
- AI recommendations should be reviewed manually.

---
