"""
AI Resume Reviewer — Powered by Groq (Llama 3.3 70B) & IBM Docling
A professional, performant Streamlit application for AI-powered resume analysis.
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

load_dotenv()

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
# Global CSS Styling
# ──────────────────────────────────────────────
st.markdown("""
<style>
  [data-testid="stAppViewContainer"] {
      background: #f0f4f8;
      color: #1e293b;
  }
  [data-testid="stHeader"] {
      background: transparent;
  }
  [data-testid="block-container"] {
      padding-top: 1rem;
      padding-bottom: 2rem;
  }
  html, body, [class*="css"] {
      color: #1e293b !important;
  }
  .card {
      background: #ffffff;
      border-radius: 12px;
      padding: 1.2rem 1.4rem;
      box-shadow: 0 1px 4px rgba(0,0,0,.07);
      margin-bottom: 0.8rem;
  }
  .card-title {
      font-size: 0.78rem;
      font-weight: 600;
      color: #64748b !important;
      text-transform: uppercase;
      letter-spacing: .06em;
      margin-bottom: .3rem;
  }
  .card-value {
      font-size: 2rem;
      font-weight: 700;
      color: #1e293b !important;
      line-height: 1;
  }
  .card-sub {
      font-size: 0.8rem;
      color: #94a3b8 !important;
      margin-top: .3rem;
  }
  .hero {
      background: linear-gradient(135deg, #1e40af 0%, #3b82f6 60%, #60a5fa 100%);
      border-radius: 16px;
      padding: 2rem 2.4rem;
      color: white !important;
      margin-bottom: 1.4rem;
  }
  .hero h1 {
      font-size: 2.1rem;
      font-weight: 800;
      color: white !important;
      margin: 0 0 .4rem;
  }
  .hero p {
      font-size: 1rem;
      color: white !important;
      opacity: .9;
      margin: 0 0 0.8rem;
  }
  .badge {
      display: inline-block;
      background: rgba(255,255,255,.2);
      color: white !important;
      border: 1px solid rgba(255,255,255,.35);
      border-radius: 20px;
      padding: .25rem .8rem;
      font-size: .78rem;
      font-weight: 600;
  }
  .section-heading {
      font-size: 1.1rem;
      font-weight: 700;
      color: #1e293b !important;
      margin: 1rem 0 .5rem;
      border-left: 4px solid #3b82f6;
      padding-left: .65rem;
  }
  div.stButton > button {
      background: #2563eb !important;
      color: white !important;
      border: none;
      border-radius: 8px;
      padding: .6rem 1.8rem;
      font-weight: 600;
      font-size: 1rem;
      width: 100%;
  }
  div.stButton > button:hover {
      background: #1d4ed8 !important;
  }
</style>
""", unsafe_allow_html=True)


# ──────────────────────────────────────────────
# PDF text extraction — IBM Docling (Cached)
# ──────────────────────────────────────────────
@st.cache_resource(show_spinner=False)
def get_docling_converter():
    """Cache the heavy Docling converter instance."""
    from docling.document_converter import DocumentConverter
    return DocumentConverter()

def extract_text_docling(pdf_bytes: bytes) -> str:
    """Extract text from a PDF using IBM Docling with PyPDF fallback."""
    try:
        converter = get_docling_converter()
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(pdf_bytes)
            tmp_path = tmp.name

        result = converter.convert(tmp_path)
        os.unlink(tmp_path)
        return result.document.export_to_markdown().strip()

    except Exception as exc:
        st.warning(f"Docling extraction note: {exc}. Falling back to standard PDF extractor.")
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
# Groq API Inference
# ──────────────────────────────────────────────
def build_analysis_prompt(resume_text: str, job_description: str) -> str:
    return f"""You are an expert HR analyst and ATS parsing system.

Analyze the resume against the job description. Return STRICTLY raw JSON matching this structure perfectly.

Resume:
\"\"\"
{resume_text[:2500]}
\"\"\"

Job Description:
\"\"\"
{job_description[:1000]}
\"\"\"

Expected JSON Output:
{{
  "overall_score": <integer 0-100>,
  "ats_score": <integer 0-100>,
  "skills_match_percent": <integer 0-100>,
  "missing_keywords": [<max 5 important keywords missing>],
  "strengths": [<max 3 concise positive points>],
  "weaknesses": [<max 3 concise negative/improvement points>],
  "section_scores": {{
    "Summary": <0-100>,
    "Experience": <0-100>,
    "Education": <0-100>,
    "Skills": <0-100>,
    "Formatting": <0-100>
  }},
  "extracted_info": {{
    "technical_skills": [<max 8 technical skills>],
    "soft_skills": [<max 5 soft skills>],
    "education": [<max 2 degree names>]
  }},
  "resume_summary": "<2 sentence overall summary>",
  "improvement_suggestions": [<max 3 clear, actionable edits>],
  "recommendation": "<Strong Match, Moderate Match, or Weak Match>",
  "recommendation_reason": "<1 sentence explanation>"
}}
"""

def call_groq(prompt: str, api_key: str, model_id: str) -> dict:
    """Execute Groq Llama 3 API call with structured JSON enforcing."""
    from groq import Groq
    
    client = Groq(api_key=api_key)
    response = client.chat.completions.create(
        model=model_id,
        messages=[
            {"role": "system", "content": "You are a precise HR evaluator that only outputs structured raw JSON."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.2,
        response_format={"type": "json_object"}
    )
    
    raw_text = response.choices[0].message.content
    return json.loads(raw_text)


# ──────────────────────────────────────────────
# Plotly Chart Helpers
# ──────────────────────────────────────────────
CHART_CONFIG = {"displayModeBar": False}

def score_color(score: int) -> str:
    if score >= 70:
        return "#16a34a"
    elif score >= 40:
        return "#ca8a04"
    return "#dc2626"

def gauge_chart(value: int, title: str, color: str = "#3b82f6") -> go.Figure:
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        title={"text": title, "font": {"size": 13, "color": "#374151"}},
        number={"font": {"size": 28, "color": "#1e293b"}},
        gauge={
            "axis": {"range": [0, 100], "tickwidth": 1, "tickcolor": "#d1d5db"},
            "bar": {"color": color},
            "bgcolor": "#f3f4f6",
            "borderwidth": 0,
            "steps": [
                {"range": [0, 40], "color": "#fee2e2"},
                {"range": [40, 70], "color": "#fef9c3"},
                {"range": [70, 100], "color": "#dcfce7"},
            ],
        },
    ))
    fig.update_layout(height=180, margin=dict(t=30, b=10, l=20, r=20), paper_bgcolor="white", plot_bgcolor="white")
    return fig

def radar_chart(categories: list, values: list) -> go.Figure:
    cats = categories + [categories[0]]
    vals = values + [values[0]]
    fig = go.Figure(go.Scatterpolar(
        r=vals, theta=cats,
        fill="toself",
        fillcolor="rgba(59,130,246,0.18)",
        line=dict(color="#3b82f6", width=2),
        marker=dict(color="#1d4ed8", size=5),
    ))
    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 100], tickfont=dict(size=9), gridcolor="#e5e7eb"),
            angularaxis=dict(tickfont=dict(size=10)),
            bgcolor="white",
        ),
        showlegend=False,
        height=260,
        margin=dict(t=20, b=20, l=35, r=35),
        paper_bgcolor="white",
    )
    return fig


# ──────────────────────────────────────────────
# Export Generators
# ──────────────────────────────────────────────
def build_pdf_report(data: dict, resume_name: str) -> bytes:
    try:
        from fpdf import FPDF
        class PDF(FPDF):
            def header(self):
                self.set_fill_color(30, 64, 175)
                self.rect(0, 0, 210, 16, "F")
                self.set_font("Helvetica", "B", 12)
                self.set_text_color(255, 255, 255)
                self.set_y(3)
                self.cell(0, 10, "AI Resume Analysis Report", align="C")
                self.ln(12)

        pdf = PDF()
        pdf.add_page()
        pdf.set_font("Helvetica", "", 10)
        pdf.set_text_color(30, 41, 59)
        
        pdf.multi_cell(0, 6, f"Resume File: {resume_name}")
        pdf.multi_cell(0, 6, f"Overall Score: {data.get('overall_score')}/100 | ATS Score: {data.get('ats_score')}/100")
        pdf.multi_cell(0, 6, f"Recommendation: {data.get('recommendation')} - {data.get('recommendation_reason')}\n\n")
        
        pdf.set_font("Helvetica", "B", 11)
        pdf.cell(0, 6, "Strengths:", ln=True)
        pdf.set_font("Helvetica", "", 10)
        for item in data.get("strengths", []):
            pdf.multi_cell(0, 6, f"- {item}")
            
        pdf.ln(3)
        pdf.set_font("Helvetica", "B", 11)
        pdf.cell(0, 6, "Actionable Improvements:", ln=True)
        pdf.set_font("Helvetica", "", 10)
        for item in data.get("improvement_suggestions", []):
            pdf.multi_cell(0, 6, f"- {item}")
            
        return bytes(pdf.output())
    except Exception:
        return json.dumps(data, indent=2).encode("utf-8")


# ──────────────────────────────────────────────
# Main Application Streamlit UI
# ──────────────────────────────────────────────
def main():
    # ── Hero ──
    st.markdown("""
    <div class="hero">
      <h1>📄 AI Resume Reviewer</h1>
      <p>Instant ATS evaluation, keyword gap identification, and structural scoring.</p>
      <span class="badge">⚡ Powered by Groq (Llama 3.3 70B) & IBM Docling</span>
    </div>
    """, unsafe_allow_html=True)

    # ── Safe Secrets Reader ──
    default_key = ""
    try:
        default_key = st.secrets.get("GROQ_API_KEY", os.getenv("GROQ_API_KEY", ""))
    except Exception:
        default_key = os.getenv("GROQ_API_KEY", "")

    # ── Sidebar ──
    with st.sidebar:
        st.markdown("### ⚙️ Configuration")
        api_key = st.text_input("Groq API Key", value=default_key, type="password")
        model_id = st.selectbox("Model", ["llama-3.3-70b-versatile", "llama3-8b-8192"])

    # ── Upload & Input ──
    col_up, col_jd = st.columns([1, 1], gap="medium")

    with col_up:
        st.markdown('<div class="section-heading">Resume Upload</div>', unsafe_allow_html=True)
        uploaded_file = st.file_uploader("Upload Resume (PDF)", type=["pdf"])
        if uploaded_file:
            st.caption(f"✅ {uploaded_file.name} ({uploaded_file.size / 1024:.1f} KB)")

    with col_jd:
        st.markdown('<div class="section-heading">Job Description</div>', unsafe_allow_html=True)
        job_desc = st.text_area("Paste Job Requirements", height=140, placeholder="Paste job specs here...")

    # ── Action Button ──
    st.markdown("")
    if st.button("🔍 Analyze Resume", use_container_width=True):
        if not uploaded_file or not job_desc.strip():
            st.error("Please upload a PDF resume and enter a job description.")
            st.stop()
        if not api_key:
            st.error("Groq API Key missing! Set `GROQ_API_KEY` in Streamlit Secrets or sidebar.")
            st.stop()

        # Extract Text
        with st.status("🔬 Extracting resume content (IBM Docling)...", expanded=False) as status:
            pdf_bytes = uploaded_file.read()
            resume_text = extract_text_docling(pdf_bytes)
            status.update(label="✅ Resume text extracted", state="complete")

        if not resume_text:
            st.error("Could not extract readable text from PDF.")
            st.stop()

        # Run AI Call
        with st.status("🤖 Evaluation in progress (Groq Llama 3.3)...", expanded=False) as status:
            try:
                prompt = build_analysis_prompt(resume_text, job_desc)
                result = call_groq(prompt, api_key, model_id)
                status.update(label="✅ Evaluation complete!", state="complete")
            except Exception as exc:
                status.update(label="❌ API Error", state="error")
                st.error(f"Groq API Execution Error: {exc}")
                st.stop()

        st.session_state["result"] = result
        st.session_state["resume_name"] = uploaded_file.name

    # ──────────────────────────────────────────────
    # Clean Compact Dashboard Renderer
    # ──────────────────────────────────────────────
    result = st.session_state.get("result")
    if not result:
        st.divider()
        st.info("👆 Upload your resume and paste a job description to generate the dashboard.")
        return

    st.divider()
    st.markdown('<div class="section-heading">📊 Evaluation Results</div>', unsafe_allow_html=True)

    # 1. Headline Score Metrics Cards
    m1, m2, m3, m4 = st.columns(4, gap="small")
    overall = result.get("overall_score", 0)
    ats = result.get("ats_score", 0)
    skills = result.get("skills_match_percent", 0)
    missing_count = len(result.get("missing_keywords", []))

    with m1:
        st.markdown(f'<div class="card" style="border-top:4px solid {score_color(overall)}"><div class="card-title">Overall Score</div><div class="card-value">{overall}%</div></div>', unsafe_allow_html=True)
    with m2:
        st.markdown(f'<div class="card" style="border-top:4px solid {score_color(ats)}"><div class="card-title">ATS Score</div><div class="card-value">{ats}%</div></div>', unsafe_allow_html=True)
    with m3:
        st.markdown(f'<div class="card" style="border-top:4px solid {score_color(skills)}"><div class="card-title">Skills Match</div><div class="card-value">{skills}%</div></div>', unsafe_allow_html=True)
    with m4:
        st.markdown(f'<div class="card" style="border-top:4px solid #ef4444"><div class="card-title">Missing Keywords</div><div class="card-value">{missing_count}</div></div>', unsafe_allow_html=True)

    # 2. Executive Recommendation Callout
    rec = result.get("recommendation", "Notice")
    st.info(f"**Hiring Status Recommendation:** {rec} — {result.get('recommendation_reason', '')}")

    # 3. Compact Visualizations Row
    st.markdown('<div class="section-heading">📈 Visual Breakdown</div>', unsafe_allow_html=True)
    c_gauge, c_radar = st.columns([1, 1], gap="medium")

    with c_gauge:
        st.plotly_chart(gauge_chart(overall, "Overall Score Gauge", score_color(overall)), use_container_width=True, config=CHART_CONFIG)

    with c_radar:
        scores_dict = result.get("section_scores", {})
        if scores_dict:
            fig_radar = radar_chart(list(scores_dict.keys()), list(scores_dict.values()))
            st.plotly_chart(fig_radar, use_container_width=True, config=CHART_CONFIG)

    # 4. Detailed Structured Insights in Tabs (Keeps height short)
    tab_eval, tab_gaps, tab_parsed = st.tabs(["🎯 Strengths & Growth", "⚠️ Missing Keywords", "📋 Extracted Details"])

    with tab_eval:
        col_s, col_w = st.columns(2)
        with col_s:
            st.markdown("**Strengths**")
            for item in result.get("strengths", []):
                st.write(f"• {item}")
        with col_w:
            st.markdown("**Areas for Growth**")
            for item in result.get("weaknesses", []):
                st.write(f"• {item}")

    with tab_gaps:
        m_keywords = result.get("missing_keywords", [])
        if m_keywords:
            st.write("Identified keyword gaps relative to the job description:")
            st.write(" ".join([f"`{kw}`" for kw in m_keywords]))
        else:
            st.success("No major keyword gaps identified!")

    with tab_parsed:
        ext = result.get("extracted_info", {})
        st.write("**Technical Skills:**", ", ".join(ext.get("technical_skills", [])) or "None extracted")
        st.write("**Soft Skills:**", ", ".join(ext.get("soft_skills", [])) or "None extracted")
        st.write("**Education:**", ", ".join(ext.get("education", [])) or "None extracted")

    # 5. Expandable Action Items & Downloads
    with st.expander("💡 View Detailed Actionable Resume Improvement Suggestions"):
        for sug in result.get("improvement_suggestions", []):
            st.write(f"👉 {sug}")

    st.markdown("---")
    dl_pdf, dl_json = st.columns(2)

    with dl_pdf:
        pdf_data = build_pdf_report(result, st.session_state.get("resume_name", "Resume"))
        st.download_button(
            label="📥 Download PDF Summary Report",
            data=pdf_data,
            file_name="resume_analysis_report.pdf",
            mime="application/pdf",
            use_container_width=True,
        )

    with dl_json:
        st.download_button(
            label="📄 Download Raw Data (JSON)",
            data=json.dumps(result, indent=2),
            file_name="resume_analysis.json",
            mime="application/json",
            use_container_width=True,
        )

if __name__ == "__main__":
    main()
