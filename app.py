"""
AI Resume Reviewer — Powered by Groq (Llama 3.3 70B) & IBM Docling
Fixed Schema & Single Visual Dashboard
"""

import os
import io
import json
import tempfile
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
# CSS Styling
# ──────────────────────────────────────────────
st.markdown("""
<style>
  [data-testid="stAppViewContainer"] {
      background: #f8fafc;
      color: #0f172a;
  }
  .card {
      background: #ffffff;
      border-radius: 10px;
      padding: 1rem 1.2rem;
      box-shadow: 0 2px 8px rgba(0,0,0,0.06);
      border: 1px solid #e2e8f0;
  }
  .card-title {
      font-size: 0.8rem;
      font-weight: 700;
      color: #64748b;
      text-transform: uppercase;
      margin-bottom: 0.2rem;
  }
  .card-value {
      font-size: 2.2rem;
      font-weight: 800;
      color: #0f172a;
      line-height: 1;
  }
  .hero {
      background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
      border-radius: 12px;
      padding: 1.8rem;
      color: white !important;
      margin-bottom: 1.2rem;
  }
  .hero h1 { color: white !important; margin: 0; font-size: 2rem; font-weight: 800; }
  .hero p { color: #e2e8f0 !important; margin: 0.3rem 0 0 0; }
</style>
""", unsafe_allow_html=True)


# ──────────────────────────────────────────────
# PDF Text Extraction
# ──────────────────────────────────────────────
@st.cache_resource(show_spinner=False)
def get_docling_converter():
    from docling.document_converter import DocumentConverter
    return DocumentConverter()

def extract_text_docling(pdf_bytes: bytes) -> str:
    try:
        converter = get_docling_converter()
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(pdf_bytes)
            tmp_path = tmp.name

        result = converter.convert(tmp_path)
        os.unlink(tmp_path)
        return result.document.export_to_markdown().strip()
    except Exception:
        return extract_text_fallback(pdf_bytes)

def extract_text_fallback(pdf_bytes: bytes) -> str:
    try:
        import pypdf
        reader = pypdf.PdfReader(io.BytesIO(pdf_bytes))
        return "\n".join([page.extract_text() or "" for page in reader.pages]).strip()
    except Exception:
        return ""


# ──────────────────────────────────────────────
# Groq Inference (Strict Schema)
# ──────────────────────────────────────────────
def call_groq_analysis(resume_text: str, job_description: str, api_key: str, model_id: str) -> dict:
    from groq import Groq
    client = Groq(api_key=api_key)

    prompt = f"""
Analyze this resume against the job description. Return STRICT raw JSON with exact keys.

Resume:
{resume_text[:3000]}

Job Description:
{job_description[:1200]}

Output MUST be valid JSON with this EXACT key structure:
{{
  "overall_score": 82,
  "ats_score": 78,
  "skills_match_percent": 85,
  "missing_keywords": ["Kubernetes", "GraphQL", "CI/CD"],
  "section_scores": {{
    "Summary": 80,
    "Experience": 85,
    "Education": 90,
    "Skills": 75,
    "Formatting": 88
  }},
  "strengths": ["Strong background in data modeling", "Clear quantifiable metrics in experience"],
  "weaknesses": ["Lacks cloud platform explicit mentions", "Short project descriptions"],
  "extracted_info": {{
    "technical_skills": ["Python", "SQL", "PyTorch", "Docker"],
    "soft_skills": ["Leadership", "Communication"],
    "education": ["B.S. Computer Science"]
  }},
  "improvement_suggestions": [
    "Add AWS/GCP certification or project details to match job spec",
    "Quantify leadership achievements with team sizes"
  ],
  "recommendation": "Moderate Match",
  "recommendation_reason": "Strong data science skill alignment but needs explicit cloud/NLP context."
}}
"""

    response = client.chat.completions.create(
        model=model_id,
        messages=[
            {"role": "system", "content": "You are a precise resume parser. Output strictly structured valid JSON."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.1,
        response_format={"type": "json_object"}
    )

    return json.loads(response.choices[0].message.content)


# ──────────────────────────────────────────────
# Visual Plot Helpers (SINGLE Chart Instances)
# ──────────────────────────────────────────────
def make_gauge_chart(score: int) -> go.Figure:
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        title={"text": "Overall Score Match", "font": {"size": 14, "color": "#475569"}},
        number={"font": {"size": 32, "color": "#0f172a"}},
        gauge={
            "axis": {"range": [0, 100]},
            "bar": {"color": "#2563eb"},
            "steps": [
                {"range": [0, 40], "color": "#fee2e2"},
                {"range": [40, 70], "color": "#fef9c3"},
                {"range": [70, 100], "color": "#dcfce7"}
            ]
        }
    ))
    fig.update_layout(height=200, margin=dict(t=30, b=10, l=25, r=25), paper_bgcolor="white")
    return fig

def make_single_radar(scores_dict: dict) -> go.Figure:
    categories = list(scores_dict.keys())
    values = list(scores_dict.values())
    
    # Close the polygon loop
    categories += [categories[0]]
    values += [values[0]]

    fig = go.Figure(go.Scatterpolar(
        r=values,
        theta=categories,
        fill="toself",
        fillcolor="rgba(37, 99, 235, 0.2)",
        line=dict(color="#2563eb", width=2),
        marker=dict(size=6, color="#1d4ed8")
    ))
    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 100], tickfont=dict(size=10)),
            angularaxis=dict(tickfont=dict(size=11, color="#334155"))
        ),
        showlegend=False,
        height=240,
        margin=dict(t=20, b=20, l=40, r=40),
        paper_bgcolor="white"
    )
    return fig


# ──────────────────────────────────────────────
# Main Application UI
# ──────────────────────────────────────────────
def main():
    st.markdown("""
    <div class="hero">
      <h1>📄 AI Resume Analyzer</h1>
      <p>Instant scoring, ATS keyword analysis, and actionable feedback.</p>
    </div>
    """, unsafe_allow_html=True)

    default_key = st.secrets.get("GROQ_API_KEY", os.getenv("GROQ_API_KEY", ""))

    with st.sidebar:
        st.header("⚙️ Settings")
        api_key = st.text_input("Groq API Key", value=default_key, type="password")
        model_id = st.selectbox("Model", ["llama-3.3-70b-versatile", "llama3-8b-8192"])

    col1, col2 = st.columns(2)
    with col1:
        uploaded_file = st.file_uploader("Upload Resume (PDF)", type=["pdf"])
    with col2:
        job_desc = st.text_area("Paste Job Requirements", height=130)

    if st.button("🔍 Analyze Resume", use_container_width=True):
        if not uploaded_file or not job_desc.strip():
            st.error("Please provide both a PDF resume and job description.")
            st.stop()
        if not api_key:
            st.error("Groq API Key is required.")
            st.stop()

        with st.spinner("Extracting text and running evaluation..."):
            pdf_bytes = uploaded_file.read()
            text = extract_text_docling(pdf_bytes)
            if not text:
                st.error("Could not read text from uploaded PDF.")
                st.stop()

            res = call_groq_analysis(text, job_desc, api_key, model_id)
            st.session_state["analysis_res"] = res

    # ──────────────────────────────────────────────
    # RENDER DASHBOARD RESULTS
    # ──────────────────────────────────────────────
    res = st.session_state.get("analysis_res")
    if not res:
        st.info("Upload a resume and click 'Analyze Resume' to see results.")
        return

    st.markdown("---")
    st.subheader("📊 Executive Summary")

    # 1. Metric Cards Row
    c1, c2, c3, c4 = st.columns(4)
    overall = res.get("overall_score", 0)
    ats = res.get("ats_score", 0)
    skills = res.get("skills_match_percent", 0)
    missing_kws = res.get("missing_keywords", [])

    with c1:
        st.markdown(f'<div class="card"><div class="card-title">Overall Score</div><div class="card-value" style="color:#2563eb">{overall}%</div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="card"><div class="card-title">ATS Match</div><div class="card-value" style="color:#16a34a">{ats}%</div></div>', unsafe_allow_html=True)
    with c3:
        st.markdown(f'<div class="card"><div class="card-title">Skills Match</div><div class="card-value" style="color:#0284c7">{skills}%</div></div>', unsafe_allow_html=True)
    with c4:
        st.markdown(f'<div class="card"><div class="card-title">Missing Keywords</div><div class="card-value" style="color:#dc2626">{len(missing_kws)}</div></div>', unsafe_allow_html=True)

    st.markdown("")
    st.info(f"**Recommendation:** {res.get('recommendation', 'N/A')} — {res.get('recommendation_reason', '')}")

    # 2. Charts Row (Explicit 1 Gauge + 1 Radar)
    st.subheader("📈 Visual Breakdown")
    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        st.plotly_chart(make_gauge_chart(overall), use_container_width=True, config={"displayModeBar": False})

    with chart_col2:
        sec_scores = res.get("section_scores", {})
        if sec_scores:
            st.plotly_chart(make_single_radar(sec_scores), use_container_width=True, config={"displayModeBar": False})

    # 3. Compact Details in Tabs
    st.subheader("📝 Analysis Details")
    tab1, tab2, tab3 = st.tabs(["🎯 Strengths & Weaknesses", "⚠️ Missing Keywords", "📋 Extracted Details"])

    with tab1:
        col_s, col_w = st.columns(2)
        with col_s:
            st.markdown("**Key Strengths**")
            for item in res.get("strengths", []):
                st.write(f"• {item}")
        with col_w:
            st.markdown("**Areas for Improvement**")
            for item in res.get("weaknesses", []):
                st.write(f"• {item}")

    with tab2:
        if missing_kws:
            st.write("Target these keywords from the job description:")
            st.write(" ".join([f"`{kw}`" for kw in missing_kws]))
        else:
            st.success("No missing key terms found!")

    with tab3:
        ext = res.get("extracted_info", {})
        st.write("**Technical Skills:**", ", ".join(ext.get("technical_skills", [])))
        st.write("**Soft Skills:**", ", ".join(ext.get("soft_skills", [])))
        st.write("**Education:**", ", ".join(ext.get("education", [])))

    # 4. Action Items Expander
    with st.expander("💡 View Recommended Resume Edits"):
        for sug in res.get("improvement_suggestions", []):
            st.write(f"👉 {sug}")

if __name__ == "__main__":
    main()
