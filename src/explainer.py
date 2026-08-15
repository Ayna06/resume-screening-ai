"""
explainer.py
Optional "v2" feature: uses an LLM to generate a short, human-readable
explanation of why a candidate does or doesn't match a job description.
"""

import os
import streamlit as st
try:
    from google import genai
    _SDK_AVAILABLE = True
except ImportError:
    _SDK_AVAILABLE = False

def get_api_key():
    # Streamlit Cloud securely stores keys in st.secrets
    if "GEMINI_API_KEY" in st.secrets:
        return st.secrets["GEMINI_API_KEY"]
    return None

def is_available() -> bool:
    return _SDK_AVAILABLE and bool(get_api_key())

def explain_match(job_description: str, resume_text: str, score: float,
                   matched_skills: list, missing_skills: list) -> str:
    if not is_available():
        return "LLM explanations are disabled (no API key configured)."

    # Grab the hidden key safely
    api_key = get_api_key()
    client = genai.Client(api_key=api_key)

    prompt = f"""You are assisting a recruiter. Based on the job description and
resume excerpt below, write a concise, factual, 2-3 sentence explanation of why
this candidate is or isn't a strong match. Be specific and evidence-based.
Do not invent experience that isn't stated in the resume.

Match score: {score}/100
Matched skills: {", ".join(matched_skills) or "none detected"}
Missing skills: {", ".join(missing_skills) or "none"}

Job description:
{job_description[:1500]}

Resume:
{resume_text[:1500]}
"""
    try:
        # NEW SDK GENERATION SYNTAX
        response = client.models.generate_content(
            model='gemini-3.5-flash-lite',
            contents=prompt
        )
        return response.text.strip()
    except Exception as e:
        error_msg = str(e)
        # Check if the error is the rate limit (429)
        if "429" in error_msg or "RESOURCE_EXHAUSTED" in error_msg:
            return "The AI is currently processing high traffic on the free tier. Please wait about 60 seconds and try again ✨"
        
        # Fallback for any other random API errors
        return "⚠️ AI insights are temporarily unavailable. Please try again later."