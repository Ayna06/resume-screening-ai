"""
scorer.py
Scores resumes against a job description using a blend of:
  1. Semantic similarity via sentence embeddings (captures meaning —
     "quick" and "fast" score as similar even though they share no letters), and
  2. Explicit skill-overlap ratio (captures how many *required* skills
     from the job description are literally present in the resume).

Why embeddings instead of TF-IDF: TF-IDF only matches identical words. It
cannot tell that "led a team" and "managed a team" mean the same thing, or
that "quick" and "fast" are synonyms. Sentence embeddings (via
`sentence-transformers`) encode each document as a dense vector trained so
that semantically similar text ends up close together in vector space,
regardless of exact wording — a much closer match to how a human reviewer
actually reads a resume.

Model: all-MiniLM-L6-v2 — a small, fast, CPU-friendly sentence-transformer
model that is a common industry-standard choice for this kind of semantic
similarity task.
"""

# from functools import lru_cache
import streamlit as st
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

from .preprocessing import clean_text, extract_skills

# How much weight the skill-overlap ratio gets vs. semantic similarity.
# 0.0 = pure embeddings, 1.0 = pure skill matching.
SKILL_WEIGHT = 0.5
TEXT_WEIGHT = 1 - SKILL_WEIGHT

MODEL_NAME = "all-MiniLM-L6-v2"

# Sentence-transformer models have a max input length (this model: 256
# word-pieces). Longer resumes get truncated by the model automatically,
# but we cap here too so encoding stays fast and predictable.
MAX_CHARS = 4000


# @lru_cache(maxsize=1)
@st.cache_resource
def _get_model():
    """
    Load the embedding model once and cache it. Loading is the slow part
    (a few seconds); encoding individual documents afterward is fast.
    lru_cache keeps this to a single load per process, which matters a lot
    in Streamlit since app.py reruns top-to-bottom on every interaction.
    """
    return SentenceTransformer(MODEL_NAME)


def score_resumes(job_description: str, resumes: dict) -> list:
    """
    job_description: raw text of the job description
    resumes: dict of {candidate_name: raw_resume_text}

    Returns a list of dicts, sorted by score descending:
        [{"name": ..., "score": ..., "text_similarity": ..., "skill_match_ratio": ...,
          "matched_skills": [...], "missing_skills": [...]}, ...]
    """
    model = _get_model()

    jd_clean = clean_text(job_description)[:MAX_CHARS]
    jd_skills = set(extract_skills(job_description))

    names = list(resumes.keys())
    resume_texts_clean = [clean_text(resumes[n])[:MAX_CHARS] for n in names]

    # Encode job description + all resumes together in one batch (faster
    # than encoding one at a time).
    all_texts = [jd_clean] + resume_texts_clean
    embeddings = model.encode(all_texts, convert_to_numpy=True, show_progress_bar=False)

    jd_embedding = embeddings[0:1]
    resume_embeddings = embeddings[1:]

    text_similarities = cosine_similarity(jd_embedding, resume_embeddings)[0]

    results = []
    for name, text_sim in zip(names, text_similarities):
        resume_skills = set(extract_skills(resumes[name]))
        matched = sorted(jd_skills & resume_skills)
        missing = sorted(jd_skills - resume_skills)

        if jd_skills:
            skill_ratio = len(matched) / len(jd_skills)
        else:
            skill_ratio = float(text_sim)

        # Cosine similarity from embeddings is typically in a narrower,
        # higher range than TF-IDF (often 0.2-0.9 even for unrelated text),
        # so clip to [0, 1] defensively before blending/display.
        text_sim_clipped = max(0.0, min(1.0, float(text_sim)))

        blended = (SKILL_WEIGHT * skill_ratio) + (TEXT_WEIGHT * text_sim_clipped)

        results.append({
            "name": name,
            "score": round(blended * 100, 2),
            "text_similarity": round(text_sim_clipped * 100, 2),
            "skill_match_ratio": round(skill_ratio * 100, 2),
            "matched_skills": matched,
            "missing_skills": missing,
        })

    results.sort(key=lambda r: r["score"], reverse=True)
    return results
