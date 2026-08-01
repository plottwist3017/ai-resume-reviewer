"""
AI Resume Reviewer — Powered by Groq (Llama 3.3) & IBM Docling
A professional Streamlit application for AI-powered resume analysis.
"""

import os
import io
import json
import re
import tempfile
import datetime
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

def _secret(key: str, default: str = "") -> str:
    """Read from st.secrets first (Streamlit Cloud), then env vars."""
    try:
        return st.secrets.get(key, os.getenv(key, default))
    except Exception:
        return os.getenv(key, default)

# ──────────────────────────────────────────────
# Page configuration
# ──────────────────────────────────────────────
st.set_page_config(
    page_title="AI Resume Reviewer",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ──────────────────────────────────────────────
# PDF text extraction — Cached IBM Docling
# ──────────────────────────────────────────────
@st.cache_resource(show_spinner=False)
def get_docling_converter():
    """Cache the DocumentConverter to avoid reloading models on every run."""
    from docling.document_converter import DocumentConverter, PdfFormatOption
    from docling.datamodel.pipeline_options import PdfPipelineOptions
    from docling.datamodel.base_models import InputFormat

    pipeline_options = PdfPipelineOptions()
    pipeline_options.do_ocr = False  # Saves RAM on free-tier servers
    pipeline_options.do_table_structure = False

    return DocumentConverter(
        format_options={
            InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
        }
    )

def extract_text_docling(pdf_bytes: bytes) -> str:
    """Extract text from a PDF using IBM Docling with a fallback."""
    try:
        converter = get_docling_converter()

        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(pdf_bytes)
            tmp_path = tmp.name

        result = converter.convert(tmp_path)
        os.unlink(tmp_path)

        text = result.document.export_to_markdown()
        return text.strip()

    except Exception as exc:
        st.warning(f"Docling extraction issue: {exc}. Using fallback extraction.")
        return extract_text_fallback(pdf_bytes)

def extract_text_fallback(pdf_bytes: bytes) -> str:
    """Fallback text extraction via pypdf."""
    try:
        import pypdf
        reader = pypdf.PdfReader(io.BytesIO(pdf_bytes))
        pages = [page.extract_text() or "" for page in reader.pages]
        return "\n".join(pages).strip()
    except Exception:
        return ""

# ──────────────────────────────────────────────
# Groq Inference
# ──────────────────────────────────────────────
def build_analysis_prompt(resume_text: str, job_description: str) -> str:
    return f"""You are an expert resume reviewer and career coach with deep knowledge of ATS systems.

Analyze the following resume against the job description provided. Return ONLY valid JSON matching the specified structure.

Resume:
\"\"\"
{resume_text[:6000]}
\"\"\"

Job Description:
\"\"\"
{job_description[:3000]}
\"\"\"

Return this exact JSON structure:
{{
  "overall_score": <integer 0-100>,
  "ats_score": <integer 0-100>,
  "skills_match_percent": <integer 0-100>,
  "missing_keywords": [<list of strings>],
  "strengths": [<list of strings>],
  "weaknesses": [<list of strings>],
  "section_scores": {{
    "Summary": <integer 0-100>,
    "Experience": <integer 0-100>,
    "Education": <integer 0-100>,
    "Skills": <integer 0-100>,
    "Formatting": <integer 0-100>,
    "Keywords": <integer 0-100>
  }},
  "skills_by_category": {{
    "Technical Skills": <integer 0-100>,
    "Soft Skills": <integer 0-100>,
    "Domain Knowledge": <integer 0-100>,
    "Tools & Platforms": <integer 0-100>
  }},
  "keyword_coverage": {{
    "Present": <integer>,
    "Missing": <integer>
  }},
  "extracted_info": {{
    "technical_skills": [<list of strings>],
    "soft_skills": [<list of strings>],
    "experience": [<list of strings>],
    "education": [<list of strings>],
    "certifications": [<list of strings>],
    "projects": [<list of strings>]
  }},
  "resume_summary": "<2-3 sentence professional assessment>",
  "grammar_suggestions": [<list of strings>],
  "improvement_suggestions": [<list of strings>],
  "recommendation": "<one of: Strong Match, Moderate Match, Weak Match>",
  "recommendation_reason": "<1-2 sentences explaining the recommendation>"
}}"""

def call_groq(prompt: str, api_key: str, model_id: str) -> dict:
    """Call Groq API using native JSON mode."""
    client = Groq(api_key=api_key)
    response = client.chat.completions.create(
        model=model_id,
        messages=[
            {"role": "system", "content": "You are a professional HR analyst that outputs strictly raw JSON."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.2,
        response_format={"type": "json_object"}
    )
    raw_text = response.choices[0].message.content
    return json.loads(raw_text)

# ──────────────────────────────────────────────
# Charting & UI Code
# ──────────────────────────────────────────────
CHART_CONFIG = {"displayModeBar": False}

def gauge_chart(value: int, title: str, color: str = "#3b82f6") -> go.Figure:
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        title={"text": title, "font": {"size": 14, "color": "#e8eaf0"}},
        number={"font": {"size": 32, "color": "#e8eaf0"}},
        gauge={
            "axis": {"range": [0, 100], "tickwidth": 1, "tickcolor": "#2e3347"},
            "bar": {"color": color},
            "bgcolor": "#1a1d27",
            "borderwidth": 0,
        },
    ))
    fig.update_layout(height=200, margin=dict(t=30, b=10, l=20, r=20), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    return fig

def main():
    st.markdown("## 📄 AI Resume Reviewer")
    st.caption("Powered by Groq (Llama 3.3 70B) & IBM Docling")

    groq_api_key = _secret("GROQ_API_KEY")

    with st.sidebar:
        st.markdown("### ⚙️ Configuration")
        api_key = st.text_input("Groq API Key", value=groq_api_key, type="password")
        model_id = st.selectbox("Model", ["llama-3.3-70b-versatile", "llama3-8b-8192"])

    col_up, col_jd = st.columns([1, 1], gap="large")

    with col_up:
        uploaded_file = st.file_uploader("Upload your PDF resume", type=["pdf"])

    with col_jd:
        job_desc = st.text_area("Paste Job Description", height=180)

    if st.button("🔍 Analyze Resume", use_container_width=True):
        if not uploaded_file or not job_desc or not api_key:
            st.error("Please provide a resume, job description, and Groq API Key.")
            st.stop()

        with st.spinner("Extracting text with IBM Docling..."):
            pdf_bytes = uploaded_file.read()
            resume_text = extract_text_docling(pdf_bytes)

        with st.spinner("Analyzing with Llama 3.3 via Groq..."):
            prompt = build_analysis_prompt(resume_text, job_desc)
            try:
                result = call_groq(prompt, api_key, model_id)
                st.session_state["result"] = result
            except Exception as e:
                st.error(f"Analysis failed: {e}")
                st.stop()

    result = st.session_state.get("result")
    if result:
        st.markdown("---")
        m1, m2, m3 = st.columns(3)
        with m1:
            st.plotly_chart(gauge_chart(result.get("overall_score", 0), "Overall Score"), use_container_width=True, config=CHART_CONFIG)
        with m2:
            st.plotly_chart(gauge_chart(result.get("ats_score", 0), "ATS Score"), use_container_width=True, config=CHART_CONFIG)
        with m3:
            st.plotly_chart(gauge_chart(result.get("skills_match_percent", 0), "Skills Match %"), use_container_width=True, config=CHART_CONFIG)

        st.markdown("### 🎯 Recommendation")
        st.info(f"**{result.get('recommendation')}**: {result.get('recommendation_reason')}")

        st.markdown("### 💡 Improvement Suggestions")
        for sug in result.get("improvement_suggestions", []):
            st.write(f"- {sug}")

if __name__ == "__main__":
    main()
