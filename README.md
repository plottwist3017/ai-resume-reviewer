# 📄 AI Resume Reviewer

> **AI-Powered ATS Resume Reviewer & Keyword Analysis Platform**

An intelligent resume optimization platform that leverages **IBM Docling**, **Groq Llama 3.3 70B**, and **interactive analytics** to evaluate resumes against job descriptions. The application provides ATS compatibility scores, keyword gap analysis, resume section evaluation, and actionable recommendations to help job seekers improve their chances of landing interviews.

---

## 🌟 Overview

Recruiters often receive hundreds of applications for a single role. Before a recruiter ever reads a resume, it is commonly filtered by an Applicant Tracking System (ATS). Many qualified candidates are rejected simply because their resumes fail to align with ATS expectations.

**AI Resume Reviewer** bridges this gap by combining modern document parsing, large language models, and data visualization into a single application that delivers meaningful insights within seconds.

The platform goes beyond simple keyword matching by evaluating resume structure, technical skills, experience quality, section completeness, and overall ATS readiness.

---

## 🎥 Demo

> Add screenshots or GIF below.

![Demo](App_demo.gif)

---

# ✨ Features

### 📄 Smart Resume Parsing

- Upload text-based PDF resumes
- Extract structured markdown using IBM Docling
- Preserve formatting for better AI understanding

---

### 🎯 ATS Keyword Analysis

- Compare resume against any job description
- Detect missing skills
- Highlight absent technologies
- Measure keyword coverage

---

### 🤖 AI Resume Evaluation

Powered by **Meta Llama 3.3 70B Versatile** via Groq.

The AI analyzes:

- Resume quality
- Experience relevance
- Technical skills
- Education
- Projects
- ATS optimization
- Professional writing quality

---

### 📊 Interactive Analytics Dashboard

Visualize resume performance using Plotly charts including:

- ATS Match Score
- Resume Readiness Gauge
- Radar Chart
- Section-wise Performance
- Keyword Coverage

---

### 💡 Actionable Suggestions

Receive personalized recommendations including:

- Resume strengths
- Weak areas
- Missing keywords
- Better bullet point suggestions
- ATS optimization tips

---

### ⚡ Fast AI Inference

Using Groq's ultra-low latency inference engine, evaluations are generated in just a few seconds.

---

# 🏗️ Architecture

```text
                  PDF Resume
                       │
                       ▼
              IBM Docling Parser
                       │
                       ▼
            Markdown/Text Extraction
                       │
                       ▼
       Resume + Job Description Prompt
                       │
                       ▼
      Groq API (Llama 3.3 70B Versatile)
                       │
                       ▼
          Structured JSON Evaluation
                       │
                       ▼
      Scoring Engine & Keyword Analysis
                       │
                       ▼
      Plotly Dashboard + AI Suggestions
```

---

# 🔍 How It Works

### Step 1

Upload a PDF resume.

---

### Step 2

Paste the desired job description.

---

### Step 3

IBM Docling extracts clean markdown from the uploaded resume.

---

### Step 4

The extracted content and job description are sent to the Groq API using a strict JSON schema prompt.

---

### Step 5

The AI returns structured analysis including:

- ATS Match Score
- Section Scores
- Missing Keywords
- Resume Strengths
- Improvement Suggestions

---

### Step 6

Interactive visualizations display the overall resume quality and ATS readiness.

# 📁 Project Structure

```text
ai-resume-reviewer/
│
├── app.py
├── requirements.txt
├── README.md
├── .env.example
│
├── .streamlit/
│   └── config.toml
│
├── assets/
│   ├── Demo.gif
│   └── screenshots/
│
└── utils/
    ├── parser.py
    ├── prompt.py
    ├── charts.py
    └── evaluator.py
```

---

# 🛠️ Technology Stack

| Category | Technology |
|------------|------------|
| Frontend | Streamlit |
| Language | Python |
| AI Model | Meta Llama 3.3 70B Versatile |
| AI Provider | Groq |
| PDF Parsing | IBM Docling |
| Environment | Python Dotenv |
| Charts | Plotly |
| Data Processing | Pandas |

---

# 🔐 Privacy

AI Resume Reviewer follows a privacy-first design.

- Resumes are processed only during the active session.
- Files are not permanently stored.
- PDF extraction occurs entirely in memory.
- AI analysis is generated in real time.

---

# 🚀 Future Improvements

- 📄 AI-generated cover letters
- 📊 Resume version comparison
- 📁 Export professional PDF reports
- 🔍 OCR support for scanned resumes
- 🌐 Multi-language resume analysis
- 💼 LinkedIn profile optimization
- 🧠 Industry-specific resume scoring
- 📈 Resume improvement tracking over time

---

# 👩‍💻 Author

## **Kavya Raval**

**Computer Science Student**

Toronto Metropolitan University

Passionate about building impactful solutions at the intersection of:

- Artificial Intelligence
- Data Analytics
- Human-Centered Technology

---

## ⭐ If you found this project useful...

Please consider giving it a **Star ⭐** on GitHub!

It helps support the project and encourages future development.
