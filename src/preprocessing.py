"""
preprocessing.py
Cleans and normalizes resume/job-description text before scoring.
Also strips common identity-revealing fields (name, email, phone) to
reduce a specific, narrow class of bias risk: the scoring model should
never see who a person is, only what they've done.

Note: this is a partial mitigation, not a guarantee of fairness. Other
signals (school names, hobbies, neighborhood, writing style) can still
correlate with protected characteristics. See README "Limitations".
"""

import re

# A small, extensible skills vocabulary. Extend this list for your domain.
COMMON_SKILLS = [
    "python", "java", "javascript", "typescript", "c++", "c#", "sql", "nosql",
    "html", "css", "react", "angular", "vue", "node.js", "django", "flask",
    "fastapi", "pandas", "numpy", "scikit-learn", "tensorflow", "pytorch",
    "keras", "aws", "azure", "gcp", "docker", "kubernetes", "git", "linux",
    "machine learning", "deep learning", "nlp", "computer vision", "data analysis",
    "data visualization", "tableau", "power bi", "excel", "airflow", "spark",
    "hadoop", "mongodb", "postgresql", "mysql", "redis", "graphql", "rest api",
    "agile", "scrum", "ci/cd", "jenkins", "terraform", "streamlit", "communication",
    "leadership", "project management",
]


def strip_pii(text: str) -> str:
    """Remove emails, phone numbers, and URLs before scoring."""
    text = re.sub(r"[\w.+-]+@[\w-]+\.[\w.-]+", " ", text)  # emails
    text = re.sub(r"(\+?\d[\d\-\s()]{7,}\d)", " ", text)   # phone numbers
    text = re.sub(r"https?://\S+", " ", text)              # URLs
    return text


def clean_text(text: str) -> str:
    """Lowercase, strip PII, remove extra whitespace/punctuation noise."""
    text = strip_pii(text)
    text = text.lower()
    text = re.sub(r"[^a-z0-9+.#\s]", " ", text)  # keep + . # for skills like c++, .net, c#
    text = re.sub(r"\s+", " ", text).strip()
    return text


def extract_skills(text: str, skills_vocab=None) -> list:
    """Return the subset of a skills vocabulary found in the given text."""
    vocab = skills_vocab or COMMON_SKILLS
    cleaned = clean_text(text)
    found = [skill for skill in vocab if skill in cleaned]
    return sorted(set(found))
