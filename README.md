# 📄 Resume Screening AI
Rank resumes against a job description in seconds — with matched/missing skill
breakdowns and optional AI-generated explanations.

## The Problem
Recruiters spend an average of just a few seconds scanning each resume. This
project automates the first pass of screening — ranking candidates against a
job description by relevance — so human reviewers can spend their time where
it matters most.

## How It Works
```
Resume (PDF/DOCX/TXT) ──┐
                         ├──▶ Text Extraction ──▶ Cleaning + PII Stripping
Job Description ────────┘                              │
                                                         ▼
                                    Sentence Embeddings (all-MiniLM-L6-v2)
                                                         │
                                                         ▼
                                          Cosine Similarity Scoring
                                                (blended with skill overlap)
                                                         │
                                                         ▼
                                Ranked Results + Skill Match Breakdown
                                                         │
                                                (optional) ▼
                                            LLM-Generated Explanation
```

1. **Extraction** — resumes (PDF/DOCX/TXT) are parsed into raw text.
2. **Cleaning** — text is lowercased, normalized, and stripped of emails,
   phone numbers, and URLs before scoring (see *Fairness* below).
3. **Scoring** — resumes and the job description are encoded into semantic
   embeddings using `sentence-transformers` (`all-MiniLM-L6-v2`) and compared
   using cosine similarity. Unlike simple keyword matching, this captures
   *meaning* — e.g. "quick" and "fast" score as similar even though they
   share no letters — because the model was trained so that semantically
   similar phrases land close together in vector space.
4. **Skill matching** — a keyword vocabulary flags which required skills
   are present or missing per candidate, and this overlap ratio is blended
   into the final score so it stays aligned with the skill breakdown shown
   in the UI.
5. **(Optional) AI explanation** — if an Anthropic API key is configured,
   each top match gets a short, evidence-based natural-language explanation
   of *why* it scored the way it did.

## Features

- 📁 Upload multiple resumes (PDF, DOCX, or TXT) at once
- 🧠 Semantic matching via sentence embeddings — understands "quick" ≈ "fast",
  not just literal keyword overlap
- 📊 Ranked match scores with a clean results table
- ✅ Matched-skill / ⚠️ missing-skill breakdown per candidate
- 🤖 Optional LLM-generated match explanations
- 🛡️ PII stripping before scoring (see Fairness section)
- ⚠️ Graceful handling of unreadable/scanned files

## Getting Started
```bash
git clone https://github.com/Ayna06/resume-screening-ai.git
cd resume-screening-ai
pip install -r requirements.txt
streamlit run app.py
```

The app will open in your browser. Try it immediately using the sample
job description and resumes in `data/`.

## Project Structure

```
resume-screening-ai/
├── app.py                   # Streamlit UI
├── src/
│   ├── parser.py             # PDF/DOCX/TXT text extraction
│   ├── preprocessing.py      # cleaning, PII stripping, skill extraction
│   ├── scorer.py              # Sentence embeddings + cosine similarity scoring
│   └── explainer.py          # LLM-based match explanation
├── data/
│   ├── sample_jobs/          # example job description
│   └── sample_resumes/       # example resumes (strong/moderate/weak match)
├── requirements.txt
└── README.md
```

## Fairness & Ethics Notes

Automated resume screening carries real bias risk, and I don't want to wave
that away. This project takes a few concrete (but partial) steps:

- **PII stripping**: emails, phone numbers, and URLs are removed from resume
  text *before* scoring, so they can't influence the match score.
- **Score, don't decide**: this tool is designed as a decision-support aid to
  help a human reviewer prioritize, not an automated accept/reject system.
  Every output should be reviewed by a person before any decision is made.

**What this does *not* solve:** names, schools, addresses, and writing style
can still be present in resume text and may correlate with protected
characteristics. A production system would need additional work — e.g.,
name/school redaction, fairness audits across demographic slices, and
human-in-the-loop review — before being used in any real hiring pipeline.

## Limitations & Future Work

- Currently English-language only
- Scanned/image-only PDFs aren't OCR'd (flagged and skipped, not silently ignored)
- Skill matching relies on a hand-curated keyword list — a future version could
  use NER or an LLM for more flexible, context-aware skill extraction
- The embedding model (`all-MiniLM-L6-v2`) is general-purpose; a domain-tuned
  or larger model could improve accuracy further at the cost of speed
- No persistent storage/database yet — everything is processed in-session

## Tech Stack

`Python` · `sentence-transformers` · `scikit-learn` · `Streamlit` · `pdfplumber` · `python-docx` · `pandas`

---

Built as a portfolio project to explore practical NLP for hiring workflows.
Feedback and PRs welcome!
