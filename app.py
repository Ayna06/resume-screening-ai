"""
app.py
Streamlit UI for the Resume Screening AI project.
"""

import streamlit as st
import pandas as pd
import io

from src.parser import extract_text, is_extraction_valid
from src.scorer import score_resumes
from src.explainer import explain_match, is_available as llm_available

st.set_page_config(page_title="Resume Screening AI", page_icon="📝", layout="wide")

# ─────────────────────────────────────────────────────────────────────────
# PDF EXTRACTION CACHE
# ─────────────────────────────────────────────────────────────────────────
@st.cache_data
def get_cached_text(file_bytes, filename):
    return extract_text(io.BytesIO(file_bytes), filename)

# ─────────────────────────────────────────────────────────────────────────
# THEME: Premium Warm SaaS Dashboard
# ─────────────────────────────────────────────────────────────────────────
st.html("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

:root {
    --bg-page: #F8F1E8;          /* Warm creamy page background */
    --bg-card: #FFFDFC;          /* Warm white container background */
    --accent-primary: #B9784F;   /* Warm terracotta/caramel */
    --accent-secondary: #EAD8C7; /* Soft beige background for icons */
    --text-main: #29231F;        /* Dark brown/charcoal text */
    --text-muted: #746B65;       /* Muted warm gray */
    --border-light: #E6D8CA;     /* Subtle beige border */
}

/* Page & Main Container */
.stApp {
    background-color: transparent !important;
    font-family: 'Inter', sans-serif;
    color: var(--text-main);
}

[data-testid="stHeader"] { background: transparent; }

/* The Main UI Container */
.block-container {
    background-color: var(--bg-card);
    border: 1px solid var(--border-light);
    border-radius: 24px;
    box-shadow: 0 12px 35px rgba(41, 35, 31, 0.04);
    padding: 2.5rem 3.5rem !important;
    margin-top: 1.5rem;
    max-width: 1150px; 
    padding-bottom: 2.5rem !important;
}
footer { visibility: hidden; }

/* Text Overrides */
h1, h2, h3, h4, h5, h6 {
    font-family: 'Inter', sans-serif !important;
    color: var(--text-main) !important;
}

/* 1. Top Header Card */
.saas-header {
    background-color: var(--bg-card);
    border: 1px solid var(--border-light);
    border-radius: 18px;
    padding: 12px 24px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    box-shadow: 0 4px 12px rgba(41, 35, 31, 0.03);
    margin-bottom: 1.5rem; 
    transition: all 0.3s ease;
}
.saas-brand { font-size: 17px; font-weight: 700; color: var(--text-main); display: flex; align-items: center; gap: 12px; }
.saas-user { font-size: 14px; color: var(--text-muted); display: flex; align-items: center; gap: 12px; font-weight: 500; }
.saas-avatar { width: 28px; height: 28px; background-color: var(--accent-secondary); border-radius: 6px; display: flex; align-items: center; justify-content: center; font-size: 13px; color: var(--text-main); font-weight: 700; }
.saas-header:hover {
    background-color: #F8F1E8;
    transform: translateX(4px);
    box-shadow: 0 4px 12px rgba(41, 35, 31, 0.04);
}
/* Icon Containers */
.icon-box {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 34px;
    height: 34px;
    background-color: var(--accent-secondary);
    border-radius: 10px;
    color: var(--text-main);
}
.section-icon {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 32px;
    height: 32px;
    background-color: var(--accent-secondary);
    color: var(--text-main);
    border-radius: 8px;
}

/* Main Title */
.saas-title { font-size: 2.2rem; font-weight: 800; color: var(--text-main); margin-bottom: 0.25rem; letter-spacing: -0.02em; line-height: 1.2; }
.saas-subtitle { font-size: 1rem; color: var(--text-muted); margin-bottom: 1.5rem; font-weight: 400; } 

/* Section Titles */
.section-title { font-size: 1.1rem; font-weight: 700; color: var(--text-main); margin-bottom: 0.75rem; display: flex; align-items: center; gap: 10px; }

/* 2. Job Description Text Area Card (FIXED BORDER BLEED) */
div[data-testid="stTextArea"] div[data-baseweb="textarea"] {
    border-radius: 14px !important;
    background-color: var(--bg-card) !important;
    border: 1px solid var(--border-light) !important;
    box-shadow: 0 4px 12px rgba(41, 35, 31, 0.03) !important;
    overflow: hidden;
}
div[data-testid="stTextArea"] div[data-baseweb="textarea"]:focus-within {
    border-color: var(--accent-primary) !important;
    box-shadow: 0 0 0 1px var(--accent-primary) !important;
}
div[data-testid="stTextArea"] textarea {
    background-color: transparent !important;
    color: var(--text-main) !important;
    padding: 1rem !important;
    font-size: 14.5px !important;
    line-height: 1.5 !important;
    border: none !important;
    box-shadow: none !important;
}

/* 3. Resumes File Uploader Card */
[data-testid="stFileUploaderDropzone"] {
    background-color: var(--bg-card) !important;
    border: 1px dashed var(--accent-primary) !important;
    border-radius: 16px !important;
    padding: 2.5rem 1.5rem !important;
    box-shadow: 0 4px 12px rgba(41, 35, 31, 0.03) !important;
    transition: all 0.2s ease;
}
[data-testid="stFileUploaderDropzone"]:hover {
    border-style: solid !important;
    background-color: #FAF5F0 !important;
}
[data-testid="stFileUploaderDropzone"] button {
    background-color: var(--accent-secondary) !important;
    color: var(--text-main) !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    padding: 0.5rem 1rem !important;
}

/* Radio Layout Spacing */
.stRadio { margin-top: 0.5rem; }
.stRadio div[role="radiogroup"] { gap: 1.5rem; }
.stRadio label { color: var(--text-main) !important; font-weight: 500 !important; font-size: 14px !important; }

/* 5. Screen Resumes Button */
.stButton > button {
    background-color: var(--accent-primary) !important;
    color: #FFFFFF !important;
    border: none !important;
    border-radius: 12px !important;
    font-weight: 600 !important;
    padding: 0.75rem !important;
    font-size: 16px !important;
    box-shadow: 0 4px 12px rgba(185, 120, 79, 0.25) !important;
    transition: all 0.2s ease !important;
}
.stButton > button:hover {
    background-color: #A06440 !important;
    transform: translateY(-2px);
    box-shadow: 0 6px 16px rgba(185, 120, 79, 0.35) !important;
}
.stButton > button:disabled {
    background-color: var(--accent-secondary) !important;
    color: var(--text-muted) !important;
    box-shadow: none !important;
    transform: none !important;
}

/* Result Cards */
.saas-card {
    background-color: var(--bg-card);
    border: 1px solid var(--border-light);
    border-radius: 16px;
    padding: 24px;
    margin-bottom: 20px;
    box-shadow: 0 4px 15px rgba(41, 35, 31, 0.03);
    box-shadow: 0 4px 15px rgba(41, 35, 31, 0.03);
    transition: all 0.3s ease;
}
.saas-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 16px 32px rgba(41, 35, 31, 0.15), 0 8px 16px rgba(185, 120, 79, 0.12);
    border-color: var(--accent-primary);
}
.saas-card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 16px;
    padding-bottom: 12px;
    border-bottom: 1px solid #F0E6DD;
}
.saas-card-title { font-size: 18px; font-weight: 700; color: var(--text-main); }
.saas-card-score { font-size: 18px; font-weight: 800; color: var(--accent-primary); background: #FDF9F5; padding: 6px 14px; border-radius: 12px; border: 1px solid var(--accent-secondary); }
.saas-metrics { font-size: 14px; color: var(--text-muted); margin-bottom: 16px; display: flex; gap: 16px; font-weight: 500; }
.saas-pill { display: inline-block; font-size: 12px; font-weight: 600; padding: 4px 10px; border-radius: 6px; margin: 3px 6px 3px 0; background-color: #E6EAE3; color: #4A6B41; }
.saas-pill.missing { background-color: #F8EAEA; color: #A54040; }
.saas-explanation { 
    margin-top: 16px; 
    padding: 16px; 
    background-color: #FDF9F5; 
    border-left: 4px solid var(--accent-primary); 
    border-radius: 8px; 
    font-size: 14px; 
    color: var(--text-main); 
    line-height: 1.6; 
    transition: all 0.3s ease; /* Added smooth transition */
}
.saas-explanation:hover {
    # background-color: #F8F1E8;
    background-color: #EDE0D2;
    transform: translateX(4px);
    box-shadow: 0 4px 12px rgba(41, 35, 31, 0.04);
}
</style>
""")

# ─────────────────────────────────────────────────────────────────────────
# NAVBAR & HERO
# ─────────────────────────────────────────────────────────────────────────
st.html("""
<div class="saas-header">
    <div class="saas-brand">
        <div class="icon-box" style="font-size: 18px;">📝</div>
        Resume Screening AI
    </div>
    <div class="saas-user">ayna-naseer <div class="saas-avatar">A</div></div>
</div>

<div class="saas-title">Resume Screening AI</div>
<div class="saas-subtitle">Upload a job description and resumes to rank candidates using semantic NLP.</div>
""")

# ─────────────────────────────────────────────────────────────────────────
# INPUTS
# ─────────────────────────────────────────────────────────────────────────
col1, col2 = st.columns([1, 1], gap="large")

with col1:
    st.html("""
    <div class="section-title">
        <div class="section-icon" style="font-size: 16px;">💼</div>
          Job Description
    </div>
    """)
    
    jd_box = st.empty()
    st.write("")
    
    jd_input_method = st.radio("Input method", ["Paste text", "Upload file"], horizontal=True, label_visibility="collapsed")
    
    job_description = ""
    
    with jd_box:
        if jd_input_method == "Paste text":
            job_description = st.text_area("Paste the job description here", height=195, label_visibility="collapsed", placeholder="Paste job description here...")
        else:
            jd_file = st.file_uploader("Upload job description", type=["pdf", "docx", "txt"], label_visibility="collapsed")
            if jd_file:
                job_description = get_cached_text(jd_file.getvalue(), jd_file.name)
                if is_extraction_valid(job_description):
                    st.success("Loaded.")

with col2:
    st.html("""
    <div class="section-title">
        <div class="section-icon" style="font-size: 16px;">📄</div>
        Resumes
    </div>
    """)
    resume_files = st.file_uploader(
        "Upload one or more resumes",
        type=["pdf", "docx", "txt"],
        accept_multiple_files=True,
        label_visibility="collapsed"
    )

    st.write("") 
    
    use_llm = False
    if resume_files and job_description:
        if llm_available():
            use_llm = st.checkbox("Generate AI explanations", value=False)

    run = st.button("🔍 Screen Resumes", type="primary", disabled=not (resume_files and job_description), use_container_width=True)

# ─────────────────────────────────────────────────────────────────────────
# RESULTS
# ─────────────────────────────────────────────────────────────────────────
if run:
    with st.spinner("Processing..."):
        resumes = {}
        skipped = []

        for f in resume_files:
            text = get_cached_text(f.getvalue(), f.name)
            if is_extraction_valid(text):
                resumes[f.name] = text
            else:
                skipped.append(f.name)

        if skipped:
            st.warning(f"Skipped {len(skipped)} unreadable file(s).")

        if not resumes:
            st.error("No valid resumes to score.")
        else:
            results = score_resumes(job_description, resumes)
            st.html('<div id="results-section"></div>')
            st.html('<div class="saas-title" style="font-size: 1.8rem; margin-top: 2.5rem; margin-bottom: 1.5rem;">Analysis Results</div>')

            for i, r in enumerate(results):
                matched_pills = "".join(f'<span class="saas-pill">{s}</span>' for s in r["matched_skills"]) or '<span style="color: #746B65; font-size: 13px;">None</span>'
                missing_pills = "".join(f'<span class="saas-pill missing">{s}</span>' for s in r["missing_skills"]) or '<span style="color: #746B65; font-size: 13px;">None</span>'

                st.html(f"""
                <div class="saas-card">
                    <div class="saas-card-header">
                        <div class="saas-card-title">{r['name']}</div>
                        <div class="saas-card-score">{r['score']}%</div>
                    </div>
                    
                    <div class="saas-metrics">
                        <span><strong>Skill Overlap:</strong> {r['skill_match_ratio']}%</span>
                        <span><strong>Semantic Similarity:</strong> {r['text_similarity']}%</span>
                    </div>
                    
                    <div style="margin-bottom: 12px;">
                        <div style="font-size: 12px; color: #746B65; margin-bottom: 6px; font-weight: 600;">MATCHED</div>
                        {matched_pills}
                    </div>
                    
                    <div>
                        <div style="font-size: 12px; color: #746B65; margin-bottom: 6px; font-weight: 600;">MISSING</div>
                        {missing_pills}
                    </div>
                """)

                if use_llm:
                    explanation = explain_match(
                        job_description,
                        resumes[r["name"]],
                        r["score"],
                        r["matched_skills"],
                        r["missing_skills"],
                    )
                    st.html(f'<div class="saas-explanation"><strong>AI Insight:</strong> {explanation}</div>')

                st.html("</div>")
        st.components.v1.html("""
            <script>
                // The script runs inside a micro-iframe, so it must look up at the parent window
                setTimeout(function() {
                    const target = window.parent.document.getElementById('results-section');
                    if (target) {
                        target.scrollIntoView({ behavior: 'smooth', block: 'start' });
                    }
                }, 800); // 800ms gives Streamlit enough time to fully draw the cards
            </script>
        """, height=0, width=0)