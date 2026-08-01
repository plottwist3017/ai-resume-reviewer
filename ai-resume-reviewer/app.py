"""
AI Resume Reviewer — Powered by Groq (Llama 3.3 70B) & IBM Docling
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
# Targeted Dark Mode CSS (Prevents Icon Corruption)
# ──────────────────────────────────────────────
st.markdown("""
<style>
  /* App Background */
  .stAppViewContainer, .stHeader {
      background-color: #0b0f19 !important;
  }
  
  /* Targeted Text Styling (Preserves native icons/arrows) */
  .stMarkdown, p, span, label, h1, h2, h3, h4 {
      color: #f8fafc;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
  }

  /* Metric Cards */
  .metric-card {
      background: #161e2e;
      border-radius: 12px;
      padding: 1.2rem;
      border: 1px solid #273549;
      box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4);
      margin-bottom: 0.5rem;
  }
  
  .metric-title {
      font-size: 0.75rem;
      font-weight: 700;
      color: #94a3b8;
      text-transform: uppercase;
      letter-spacing: 0.08em;
      margin-bottom: 0.4rem;
  }
  
  .metric-value {
      font-size: 2.2rem;
      font-weight: 800;
      line-height: 1;
  }

  /* Header Banner */
  .hero-box {
      background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
      border-radius: 14px;
      padding: 1.8rem 2rem;
      border: 1px solid #334155;
      margin-bottom: 1.5rem;
  }
  
  .hero-box h1 {
      color: #ffffff !important;
      margin: 0;
      font-size: 2.1rem;
      font-weight: 800;
  }
  
  .hero-box p {
      color: #94a3b8 !important;
      margin: 0.4rem 0 0 0;
      font-size: 0.95rem;
  }

  /* Tabs Styling */
  button[data-baseweb="tab"] {
      font-weight: 600 !important;
      font-size: 0.95rem !important;
      color: #94a3b8 !important;
  }
  button[aria-selected="true"] {
      color: #38bdf8 !important;
  }
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
# Groq Inference
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
# Dark Mode Visual Charts
# ──────────────────────────────────────────────
def make_gauge_chart(score: int) -> go.Figure:
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        title={"text": "Overall Match Score", "font": {"size": 14, "color": "#94a3b8"}},
        number={"font": {"size": 34, "color": "#ffffff"}},
        gauge={
            "axis": {"range": [0, 100], "tickcolor": "#475569"},
            "bar": {"color": "#38bdf8"},
            "bgcolor": "#161e2e",
            "borderwidth": 0,
            "steps": [
                {"range": [0, 40], "color": "#451a1a"},
                {"range": [40, 70], "color": "#42380e"},
                {"range": [70, 100], "color": "#143823"}
            ]
        }
    ))
    fig.update_layout(
        height=210, 
        margin=dict(t=30, b=10, l=25, r=25), 
        paper_bgcolor="#161e2e",
        plot_bgcolor="#161e2e"
    )
    return fig

def make_single_radar(scores_dict: dict) -> go.Figure:
    categories = list(scores_dict.keys())
    values = list(scores_dict.values())
    
    categories += [categories[0]]
    values += [values[0]]

    fig = go.Figure(go.Scatterpolar(
        r=values,
        theta=categories,
        fill="toself",
        fillcolor="rgba(56, 189, 248, 0.2)",
        line=dict(color="#38bdf8", width=2),
        marker=dict(size=6, color="#60a5fa")
    ))
    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 100], tickfont=dict(size=10, color="#94a3b8"), gridcolor="#273549"),
            angularaxis=dict(tickfont=dict(size=11, color="#f8fafc")),
            bgcolor="#161e2e"
        ),
        showlegend=False,
        height=230,
        margin=dict(t=20, b=20, l=40, r=40),
        paper_bgcolor="#161e2e"
    )
    return fig


# ──────────────────────────────────────────────
# Main Application UI
# ──────────────────────────────────────────────
def main():
    st.markdown("""
    <div class="hero-box">
      <h1>📄 AI Resume Reviewer</h1>
      <p>Instant ATS evaluation, structural analysis, and skill gap identification.</p>
    </div>
    """, unsafe_allow_html=True)

    default_key = st.secrets.get("GROQ_API_KEY", os.getenv("GROQ_API_KEY", ""))

    with st.sidebar:
        st.header("⚙️ Configuration")
        api_key = st.text_input("Groq API Key", value=default_key, type="password", key="groq_key_input")
        model_id = st.selectbox("Model", ["llama-3.3-70b-versatile", "llama3-8b-8192"], key="model_select")

    col1, col2 = st.columns(2)
    with col1:
        uploaded_file = st.file_uploader("Upload Resume (PDF)", type=["pdf"], key="resume_pdf_uploader")
    with col2:
        job_desc = st.text_area("Paste Job Requirements", height=130, placeholder="Paste job requirements here...", key="job_desc_input")

    analyze_clicked = st.button("🔍 Analyze Resume", use_container_width=True, type="primary", key="analyze_action_btn")

    if analyze_clicked:
        if not uploaded_file or not job_desc.strip():
            st.error("Please provide both a PDF resume and job description.")
            st.stop()
        if not api_key:
            st.error("Groq API Key is required.")
            st.stop()

        with st.spinner("Analyzing resume content..."):
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
        st.info("Upload a resume and click 'Analyze Resume' to display results.")
        return

    st.markdown("---")
    st.markdown("### 📊 Resume Scorecard")

    # Metric Cards
    c1, c2, c3, c4 = st.columns(4)
    overall = res.get("overall_score", 0)
    ats = res.get("ats_score", 0)
    skills = res.get("skills_match_percent", 0)
    missing_kws = res.get("missing_keywords", [])

    with c1:
        st.markdown(f'<div class="metric-card"><div class="metric-title">Overall Match</div><div class="metric-value" style="color:#60a5fa">{overall}%</div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="metric-card"><div class="metric-title">ATS Readiness</div><div class="metric-value" style="color:#4ade80">{ats}%</div></div>', unsafe_allow_html=True)
    with c3:
        st.markdown(f'<div class="metric-card"><div class="metric-title">Skills Match</div><div class="metric-value" style="color:#38bdf8">{skills}%</div></div>', unsafe_allow_html=True)
    with c4:
        st.markdown(f'<div class="metric-card"><div class="metric-title">Missing Keywords</div><div class="metric-value" style="color:#f87171">{len(missing_kws)}</div></div>', unsafe_allow_html=True)

    st.markdown("")
    st.info(f"**Recommendation:** {res.get('recommendation', 'N/A')} — {res.get('recommendation_reason', '')}")

    # Visual Charts Row
    st.markdown("### 📈 Visual Breakdown")
    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        st.plotly_chart(make_gauge_chart(overall), use_container_width=True, config={"displayModeBar": False})

    with chart_col2:
        sec_scores = res.get("section_scores", {})
        if sec_scores:
            st.plotly_chart(make_single_radar(sec_scores), use_container_width=True, config={"displayModeBar": False})

    # Tabbed Details
    st.markdown("### 📝 Detailed Insights")
    tab1, tab2, tab3 = st.tabs(["🎯 Strengths & Growth", "⚠️ Missing Keywords", "📋 Extracted Details"])

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
            st.write("Target keywords identified from the job requirements:")
            st.write(" ".join([f"`{kw}`" for kw in missing_kws]))
        else:
            st.success("No critical missing keywords identified.")

    with tab3:
        ext = res.get("extracted_info", {})
        st.write("**Technical Skills:**", ", ".join(ext.get("technical_skills", [])))
        st.write("**Soft Skills:**", ", ".join(ext.get("soft_skills", [])))
        st.write("**Education:**", ", ".join(ext.get("education", [])))

    # Action Items Collapsible
    with st.expander("💡 Actionable Edit Recommendations"):
        for sug in res.get("improvement_suggestions", []):
            st.write(f"👉 {sug}")

if __name__ == "__main__":
    main()
