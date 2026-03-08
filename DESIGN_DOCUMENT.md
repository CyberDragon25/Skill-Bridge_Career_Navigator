# Design Document: SkillBridge Career Navigator

## 1. Goal
SkillBridge Career Navigator is a lightweight prototype for helping students and early-career professionals understand how their current skills align with a target technical role and what they should learn next.

The app is designed to answer four questions:
1. What skills can be detected from the candidate’s current materials?
2. How well do those skills align with a selected role?
3. Which missing skills matter most for that role?
4. What is the shortest practical roadmap to close the gap?

## 2. Chosen Scenario
This project implements the **Skill-Bridge Career Navigator** scenario from the take-home challenge.

## 3. Product Scope
### Included
- Resume text upload/paste
- Supplemental PDF upload
- AI-first skill extraction with fallback
- Role-specific skill-gap analysis
- TF-IDF + Logistic Regression role classifier
- Skill impact simulator
- Skill demand heatmap
- AI-first roadmap generation with fallback
- Basic validation
- Unit tests

### Excluded
- Authentication
- Persistent storage
- Live scraping or real job-board integration
- Course marketplace integrations
- Production deployment

## 4. Architecture
### Frontend / App Layer
- **Streamlit** (`ui.py`)
- Handles interaction, layout, and orchestration across backend modules

### Logic Modules
- `data_loader.py`: loads skills, jobs, and sample resumes
- `validators.py`: input validation for resume text and selected role
- `skill_extractor.py`: AI-first and fallback skill extraction
- `gap_analyzer.py`: deterministic role comparison and scoring
- `roadmap_generator.py`: AI-first and fallback learning roadmap
- `pdf_parser.py`: PDF text extraction using `pypdf`
- `role_classifier.py`: TF-IDF + Logistic Regression role classifier
- `skill_impact.py`: simulates score uplift from adding missing skills
- `skill_heatmap.py`: computes role-by-skill demand matrix

### Data Layer
- `data/jobs.json`: synthetic role/job posting dataset
- `data/skills.json`: canonical allowed skills
- `data/sample_resume*.txt`: synthetic sample resumes

## 5. Technical Stack
- **Language:** Python
- **UI:** Streamlit
- **AI:** OpenAI API
- **ML:** scikit-learn (TF-IDF + Logistic Regression)
- **Data processing:** pandas
- **PDF parsing:** pypdf
- **Environment management:** python-dotenv
- **Testing:** pytest

## 6. End-to-End Flow
1. User uploads or pastes synthetic resume text.
2. User optionally uploads a supplemental PDF.
3. App merges text sources.
4. App validates input and selected role.
5. App extracts skills:
   - OpenAI first
   - Regex/alias fallback second
6. App predicts likely role fit using the ML classifier.
7. App computes gap analysis against the selected target role.
8. App simulates how adding missing skills changes match score.
9. App generates a roadmap:
   - OpenAI first
   - rules-based fallback second
10. App displays job explorer, skill demand heatmap, and transferable-skill views.

## 7. Why These Design Choices
### Why Streamlit?
Streamlit reduced time spent on frontend plumbing and allowed more effort to go into the actual problem logic, explainability, and testing. For a 4–6 hour timebox, this was a better tradeoff than building a separate frontend/backend stack.

### Why OpenAI for extraction and roadmap generation?
These two tasks benefit from flexible language understanding and summarization. AI helps with messy resume text and concise, human-readable roadmap recommendations.

### Why keep deterministic fallback logic?
The challenge explicitly asks for fallback behavior when AI is unavailable or incorrect. Deterministic fallback also improves reliability and keeps the main flow functional without external dependencies.

### Why use TF-IDF + Logistic Regression?
This model is lightweight, fast, easy to explain, and a good fit for a small text classification problem over a synthetic dataset. It is intentionally simpler than a large neural approach because speed and transparency matter more than model novelty here.

### Why avoid live scraping?
The challenge requires synthetic data only. Using a curated synthetic dataset also makes the prototype deterministic and easier to test.

## 8. Scoring Logic
### Skill Extraction
The extraction module returns:
- `skills`
- `method` (`ai` or `fallback`)
- `confidence`

### Gap Analysis
For the selected target role, the app aggregates all job postings under that role and computes:
- matching required skills
- missing required skills
- matching nice-to-have skills
- extra skills
- match percentage
- recommendation string

The missing skills are prioritized by how often they appear in the role-specific dataset.

### Skill Impact Simulation
For each missing skill, the app adds that skill to the candidate profile and recomputes the match percentage. The difference is shown as `score_gain`.

### Role Classifier
The classifier predicts the most likely role and top-3 role probabilities based on a TF-IDF representation of the synthetic job postings.

## 9. Responsible AI Considerations
- The app uses synthetic data only.
- The role classifier and heatmap describe dataset alignment, not hiring causality.
- The UI clearly allows manual review and correction of extracted skills.
- AI outputs are bounded by canonical skills and validated where possible.
- Fallback logic ensures the core flow still works when OpenAI is unavailable.

## 10. Testing Strategy
The included tests cover:
- fallback skill extraction on known technical skills
- gap analysis behavior for a realistic candidate and target role
- empty-role handling in the gap analysis module

The tests focus on deterministic paths so they do not depend on OpenAI availability.

## 11. Limitations
- Small synthetic dataset limits realism.
- No persistence or long-term user history.
- PDF extraction quality depends on the PDF structure.
- AI extraction may miss subtle skills or over-extract implied ones.
- ML role classifier is illustrative and not benchmarked on real-world data.

## 12. Future Enhancements
- Embedding-based semantic matching
- Realistic synthetic dataset generation at larger scale
- Better PDF parsing with section detection
- Resume bullet rewriting aligned to selected role
- Saved sessions and comparison history
- Exportable report for mentors or career coaches
