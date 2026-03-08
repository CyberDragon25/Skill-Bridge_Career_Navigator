# Skill-Bridge_Career_Navigator# SkillBridge Career Navigator

**Candidate Name:** Subham Bhattacharya  
**Scenario Chosen:** Skill-Bridge Career Navigator  
**Estimated Time Spent:** ~6 hours
**Youtube Video Link:** https://youtu.be/rZD-PVohfWM

SkillBridge Career Navigator is a Streamlit-based prototype that helps a student or early-career candidate understand how their current skills align with a target role. The app ingests a synthetic resume or supplemental PDF, extracts technical skills with an AI-first pipeline, compares them against a synthetic job dataset, estimates role fit with a lightweight ML classifier, and generates an actionable learning roadmap.

## Problem Statement
Students and early-career professionals often know they want a role like Cloud Engineer, Security Analyst, or Backend Engineer, but they do not know which skills matter most, which skills they already have, and which missing skills would improve their fit the fastest. Existing job boards show postings one by one, but do not provide a clear gap analysis or prioritized roadmap.

## Solution Overview
This prototype provides an end-to-end flow:
- Upload or paste a synthetic resume
- Optionally upload a supplemental analysis/portfolio PDF
- Select a target role
- Extract skills using OpenAI with a rule-based fallback
- Compare skills against a synthetic job dataset
- Predict likely best-fit role using TF-IDF + Logistic Regression
- Simulate how adding missing skills improves match score
- Generate a roadmap using OpenAI with a fallback rules engine

## Repository Structure
```text
Skill-Bridge_Career_Navigator/
├── ui.py
├── requirements.txt
├── README.md
├── DESIGN_DOCUMENT.md
├── data/
│   ├── jobs.json
│   ├── skills.json
│   ├── sample_resume1.txt
│   ├── sample_resume2.txt
│   └── sample_resume3.txt
├── src/
│   ├── data_loader.py
│   ├── validators.py
│   ├── skill_extractor.py
│   ├── gap_analyzer.py
│   ├── roadmap_generator.py
│   ├── pdf_parser.py
│   ├── role_classifier.py
│   ├── skill_impact.py
│   └── skill_heatmap.py
└── tests/
    ├── test_extraction.py
    └── test_gap_analysis.py
```

## Quick Start
### Prerequisites
- Python 3.10+
- pip
- Optional: OpenAI API key for AI extraction and AI roadmap generation

### Setup
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Environment Variables
Create a `.env` file in the project root:
```env
OPENAI_API_KEY=your_api_key_here
```

If the API key is missing or an AI call fails, the app falls back to deterministic logic.

### Run Commands
```bash
streamlit run ui.py
```

### Test Commands
```bash
pytest tests -q
```

## Core Features
### 1. End-to-End Skill Gap Analysis
The user provides resume content, chooses a target role, and receives:
- detected skills
- match score
- matching required skills
- missing required skills
- nice-to-have matches
- extra transferable skills

### 2. AI Integration + Fallback
Two AI capabilities are implemented:
- **Skill extraction** from resume and supplemental document text
- **Roadmap generation** for the top missing skills

Each has a fallback:
- Rule-based skill extraction using canonical aliases and regex
- Rule-based roadmap generation using curated default resources

### 3. Classical ML Role Classifier
A TF-IDF + Logistic Regression classifier predicts the likely best-fit role using the synthetic job dataset.

### 4. PDF Ingestion
The app accepts a supplemental PDF and extracts text locally using `pypdf`. This lets the user add portfolio writeups or analysis reports without building a full document parser pipeline.

### 5. Skill Impact Simulator
For each missing skill, the app simulates adding that skill and recomputes the role match score. This helps the user see which next skill gives the biggest improvement in dataset alignment.

### 6. Skill Demand Heatmap
The app builds an aggregate role-by-skill demand matrix over the synthetic dataset to show which skills are most common for the selected role and which skills transfer across roles.

## Synthetic Dataset
The repository uses synthetic data only:
- synthetic job postings in `data/jobs.json`
- a canonical skills list in `data/skills.json`
- sample synthetic resumes in `data/sample_resume*.txt`

No live job scraping is used.

## AI Disclosure
### Did you use an AI assistant (Copilot, ChatGPT, etc.)?
Yes.

### How did you verify the suggestions?
I reviewed generated code and text manually, ran local tests, validated output shapes across modules, and kept deterministic fallbacks for core flows.

### Give one example of a suggestion you rejected or changed
I avoided making claims like “AWS makes someone 3x more likely to get hired,” because the project only uses synthetic job-posting data, not real hiring outcome data. I replaced that with a skill-impact simulator and demand heatmap grounded in the synthetic dataset.

## Responsible AI and Security Notes
- Synthetic data only; no real personal data is required.
- AI extraction and AI roadmap generation may be imperfect.
- The user can manually review and edit extracted skills.
- The ML role classifier estimates fit on the synthetic dataset only and should not be interpreted as real-world hiring probability.
- API keys are loaded from environment variables and not committed to the repository.
- Uploaded PDFs are processed in memory for the running session; the app does not implement long-term storage.

## Tradeoffs & Prioritization
### What did you cut to stay within the 4–6 hour limit?
- Authentication and persistent user accounts
- Production deployment
- Full PDF resume parsing beyond basic text extraction
- Live job-board integration
- Course API integration
- Advanced charts and dashboards

### What would you build next if you had more time?
- Better PDF parsing and section-aware document understanding
- Resume bullet rewriting tailored to the target role
- Embeddings-based semantic skill matching
- Saved comparison history and multiple candidate profiles
- More realistic synthetic dataset generation and benchmark evaluation

### Known limitations
- The synthetic dataset is intentionally small and illustrative.
- ML role classification depends on the diversity of the synthetic dataset.
- AI outputs can fail or produce incomplete recommendations.
- PDF extraction quality depends on document formatting.
- Match score reflects dataset alignment, not hiring outcomes.
