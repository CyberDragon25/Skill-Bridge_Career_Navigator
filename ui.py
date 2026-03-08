import streamlit as st
import pandas as pd

from src.data_loader import load_jobs, load_skills, load_sample_resume, get_available_roles
from src.validators import validate_resume_text, validate_role
from src.skill_extractor import extract_skills
from src.gap_analyzer import analyze_gap_for_role
from src.roadmap_generator import generate_roadmap


# ---------- Load app data ----------
jobs = load_jobs()
skills = load_skills()
roles = get_available_roles(jobs)


# ---------- UI helpers ----------
def badge_list(items, kind="neutral"):
    color_map = {
        "good": "rgba(52,211,153,.14)",
        "bad": "rgba(248,113,113,.14)",
        "neutral": "rgba(148,163,184,.14)",
        "nice": "rgba(96,165,250,.14)",
    }
    border_map = {
        "good": "#34d399",
        "bad": "#f87171",
        "neutral": "#64748b",
        "nice": "#60a5fa",
    }
    bg = color_map.get(kind, color_map["neutral"])
    border = border_map.get(kind, border_map["neutral"])

    if not items:
        return "<span class='muted'>None yet</span>"

    return " ".join(
        [
            f"<span class='skill-pill' style='background:{bg}; border:1px solid {border};'>{item}</span>"
            for item in items
        ]
    )


def metric_card(label: str, value: str):
    st.markdown(
        f"""
        <div class="mini-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value" style="font-size:{'2rem' if len(str(value)) < 10 else '1.15rem'};">{value}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ---------- Page config ----------
st.set_page_config(
    page_title="SkillBridge Career Navigator",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ---------- Styling ----------
st.markdown(
    """
    <style>
    .stApp {
        background:
            radial-gradient(circle at top left, rgba(99,102,241,.24), transparent 24%),
            radial-gradient(circle at top right, rgba(16,185,129,.16), transparent 20%),
            linear-gradient(180deg, #0b1020 0%, #111827 38%, #0f172a 100%);
        color: #e5e7eb;
    }
    .block-container {
        padding-top: 2.2rem;
        padding-bottom: 2rem;
        max-width: 1200px;
    }
    h1, h2, h3 { color: #f8fafc !important; }
    [data-testid="stSidebar"] {
        background: rgba(15, 23, 42, .72);
        border-right: 1px solid rgba(148, 163, 184, .14);
    }
    .hero-card {
        padding: 2rem;
        border-radius: 28px;
        background: linear-gradient(135deg, rgba(17,24,39,.92), rgba(30,41,59,.82));
        border: 1px solid rgba(148,163,184,.16);
        box-shadow: 0 24px 80px rgba(0,0,0,.28);
        margin-bottom: 1rem;
    }
    .glass-card {
        padding: 1.2rem 1.2rem;
        border-radius: 22px;
        background: rgba(15,23,42,.72);
        border: 1px solid rgba(148,163,184,.14);
        box-shadow: 0 14px 40px rgba(0,0,0,.18);
        margin-bottom: 1rem;
    }
    .mini-card {
        padding: 1rem 1.1rem;
        border-radius: 20px;
        background: rgba(15,23,42,.78);
        border: 1px solid rgba(148,163,184,.14);
        min-height: 120px;
    }
    .metric-label {
        color: #94a3b8;
        font-size: .88rem;
        margin-bottom: .4rem;
    }
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        color: #f8fafc;
        line-height: 1;
    }
    .muted { color: #94a3b8; }
    .skill-pill {
        display: inline-block;
        margin: 0.2rem 0.35rem 0.2rem 0;
        padding: 0.42rem 0.7rem;
        border-radius: 999px;
        font-size: 0.88rem;
        color: #f8fafc;
        white-space: nowrap;
    }
    .section-kicker {
        letter-spacing: .08em;
        text-transform: uppercase;
        color: #93c5fd;
        font-size: .76rem;
        font-weight: 700;
    }
    .roadmap-item {
        border-left: 3px solid #818cf8;
        padding: .8rem 1rem;
        margin-bottom: .8rem;
        background: rgba(30,41,59,.6);
        border-radius: 0 16px 16px 0;
    }
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #22c55e, #3b82f6, #8b5cf6);
    }
    div[data-testid="stFileUploader"] section {
        background: rgba(15,23,42,.7);
        border-radius: 18px;
        border: 1px dashed rgba(148,163,184,.35);
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ---------- Sidebar ----------
with st.sidebar:
    st.markdown("## 🚀 SkillBridge")
    st.caption("AI-assisted career navigation demo")

    target_role = st.selectbox("Target role", roles)

    use_ai = st.toggle("Use AI where available", value=True)

    sample_resume_option = st.selectbox(
        "Sample resume",
        ["None", "sample_resume1.txt", "sample_resume2.txt", "sample_resume3.txt"],
        index=0,
    )

    show_job_explorer = st.toggle("Show job explorer", value=True)

    st.markdown("---")
    st.markdown("### Demo flow")
    st.markdown("1. Upload or paste resume")
    st.markdown("2. Pick a role")
    st.markdown("3. Analyze role fit")
    st.markdown("4. Review roadmap")


# ---------- Current role snapshot ----------
role_jobs = [job for job in jobs if job["role"] == target_role]
primary_job = role_jobs[0] if role_jobs else {
    "title": target_role,
    "description": "",
    "required_skills": [],
    "nice_to_have_skills": []
}


# ---------- Hero ----------
st.markdown(
    f"""
    <div class="hero-card">
        <div class="section-kicker">AI-assisted career planning</div>
        <h1 style="margin:.35rem 0 .6rem 0;">SkillBridge Career Navigator</h1>
        <p style="font-size:1.05rem; color:#cbd5e1; max-width:760px; margin:0;">
            Turn a resume into a clear role match, identify the most important missing skills, and generate a concise learning roadmap for <b>{target_role}</b>.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)


# ---------- Input ----------
left, right = st.columns([1.15, 0.85], gap="large")

resume_text = ""

with left:
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.markdown("### 📄 Resume Input")

    uploaded_file = st.file_uploader(
        "Upload a synthetic resume text file",
        type=["txt", "md"],
    )

    if uploaded_file is not None:
        try:
            resume_text = uploaded_file.read().decode("utf-8", errors="ignore")
        except Exception:
            resume_text = ""

    if sample_resume_option != "None" and not resume_text.strip():
        try:
            resume_text = load_sample_resume(sample_resume_option)
        except Exception:
            resume_text = ""

    pasted_resume = st.text_area(
        "Or paste resume text",
        value=resume_text,
        height=280,
        placeholder="Paste synthetic resume content here...",
    )

    if pasted_resume.strip():
        resume_text = pasted_resume

    analyze_clicked = st.button("Analyze my fit", type="primary", use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

with right:
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.markdown("### 🎯 Role Snapshot")
    st.markdown(f"**{primary_job.get('title', target_role)}**")
    st.caption(primary_job.get("description", ""))

    st.markdown("**Required skills**")
    st.markdown(
        badge_list(primary_job.get("required_skills", []), "neutral"),
        unsafe_allow_html=True,
    )

    st.markdown("**Nice to have**")
    st.markdown(
        badge_list(primary_job.get("nice_to_have_skills", []), "nice"),
        unsafe_allow_html=True,
    )

    st.markdown("</div>", unsafe_allow_html=True)


# ---------- Analysis ----------
if analyze_clicked:
    try:
        validate_resume_text(resume_text)
        validate_role(target_role, jobs)

        with st.spinner("Running AI-assisted skill gap analysis..."):
            extraction_result = extract_skills(
                text=resume_text,
                known_skills=skills,
                use_ai=use_ai
            )

            extracted_skills = extraction_result["skills"]

            gap_result = analyze_gap_for_role(
                candidate_skills=extracted_skills,
                jobs=jobs,
                role=target_role
            )

            roadmap_result = generate_roadmap(
                missing_skills=gap_result["missing_skills"],
                role=target_role,
                use_ai=use_ai
            )

        st.session_state["analysis"] = {
            "skills": extracted_skills,
            "result": gap_result,
            "roadmap": roadmap_result,
            "extraction_method": extraction_result["method"],
            "confidence": extraction_result["confidence"],
        }

    except ValueError as e:
        st.error(str(e))
    except Exception as e:
        st.error(f"Unexpected error: {e}")


# ---------- Results ----------
if "analysis" in st.session_state:
    analysis = st.session_state["analysis"]
    extracted = analysis["skills"]
    result = analysis["result"]
    roadmap = analysis["roadmap"]
    extraction_method = analysis.get("extraction_method", "fallback")
    confidence = analysis.get("confidence", "medium")

    score = result["match_percentage"]
    if score >= 80:
        status = "Application ready"
    elif score >= 60:
        status = "Close match"
    elif score >= 40:
        status = "Needs upskilling"
    else:
        status = "Needs stronger foundation"

    st.markdown("### 📊 Match Overview")
    st.caption(f"Extraction method: {extraction_method.upper()} · Confidence: {confidence.capitalize()}")

    c1, c2, c3, c4 = st.columns(4, gap="medium")
    with c1:
        metric_card("Match score", f"{score}%")
    with c2:
        metric_card("Matched skills", str(len(result["matching_skills"])))
    with c3:
        metric_card("Missing skills", str(len(result["missing_skills"])))
    with c4:
        metric_card("Status", status)

    st.progress(min(max(score / 100, 0.0), 1.0))
    st.caption(result["recommendation"])

    st.info(
        "AI-generated extraction and roadmap suggestions may be imperfect. "
        "Use the editable skills review below to correct the analysis when needed."
    )

    edited_skills = st.multiselect(
        "Review / edit extracted skills",
        options=skills,
        default=extracted,
    )

    if st.button("Re-run analysis with edited skills", use_container_width=True):
        try:
            gap_result = analyze_gap_for_role(
                candidate_skills=edited_skills,
                jobs=jobs,
                role=target_role
            )

            roadmap_result = generate_roadmap(
                missing_skills=gap_result["missing_skills"],
                role=target_role,
                use_ai=use_ai
            )

            st.session_state["analysis"] = {
                "skills": edited_skills,
                "result": gap_result,
                "roadmap": roadmap_result,
                "extraction_method": "manual-review",
                "confidence": "high",
            }

            st.success("Analysis updated with reviewed skills.")
            st.rerun()

        except Exception as e:
            st.error(f"Failed to update analysis: {e}")

    a, b = st.columns([1, 1], gap="large")

    with a:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.markdown("### ✅ Skills Overview")

        st.markdown("**Detected from resume**")
        st.markdown(badge_list(extracted, "neutral"), unsafe_allow_html=True)

        st.markdown("**Matching required skills**")
        st.markdown(badge_list(result["matching_skills"], "good"), unsafe_allow_html=True)

        st.markdown("**Matching nice-to-have skills**")
        st.markdown(badge_list(result["matching_nice_to_have"], "nice"), unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

    with b:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.markdown("### 🧩 Skill Gaps")

        missing_skill_names = [item["skill"] for item in result["missing_skills"]]

        st.markdown("**Missing required skills**")
        st.markdown(badge_list(missing_skill_names, "bad"), unsafe_allow_html=True)

        st.markdown("**Extra transferable skills**")
        st.markdown(badge_list(result["extra_skills"], "neutral"), unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

    if result["missing_skills"]:
        st.markdown("### 📌 Missing Skill Priority")
        missing_df = pd.DataFrame(result["missing_skills"])
        st.dataframe(missing_df, use_container_width=True, hide_index=True)

    st.markdown("### 🗺️ Learning Roadmap")

    if not roadmap["roadmap"]:
        st.success("No missing skills found. You appear ready for this role.")
    else:
        col_left, col_right = st.columns([1.3, 0.7], gap="large")

        with col_left:
            st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
            for idx, item in enumerate(roadmap["roadmap"], start=1):
                st.markdown(
                    f"""
                    <div class='roadmap-item'>
                        <div class='section-kicker'>Step {idx}</div>
                        <div style='font-size:1.05rem; font-weight:700; color:#f8fafc; margin:.2rem 0;'>
                            Learn {item.get('skill', 'Skill')}
                        </div>
                        <div style='color:#cbd5e1; margin-bottom:.25rem;'>
                            <b>Why it matters:</b> {item.get('why_it_matters', 'Important for the target role.')}
                        </div>
                        <div style='color:#cbd5e1;'>
                            <b>Estimated time:</b> {item.get('time', '2 weeks')}
                        </div>
                        <div style='color:#cbd5e1; margin-top:.25rem;'>
                            <b>Recommended action:</b> {item.get('resource', 'Complete one focused resource and project.')}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                if item.get("url"):
                    st.markdown(f"[Open resource]({item['url']})")

            st.markdown("</div>", unsafe_allow_html=True)

        with col_right:
            st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
            st.markdown("### Summary")
            st.metric("Estimated timeline", roadmap["estimated_total_time"])
            st.metric("Missing skills", len(result["missing_skills"]))
            st.metric("Target role", target_role)
            st.markdown("</div>", unsafe_allow_html=True)

    if show_job_explorer:
        st.markdown("### 🧾 Job Explorer")
        if role_jobs:
            job_df = pd.DataFrame(role_jobs)
            st.dataframe(job_df, use_container_width=True, hide_index=True)
        else:
            st.info("No jobs found for this role in the current dataset.")

    st.markdown("### 🪄 Suggested next improvements")
    st.info(
        "Possible next upgrades: JD upload, PDF resume parsing, embeddings-based skill extraction, "
        "resume bullet rewriting, and saved history for repeated comparisons."
    )

else:
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.markdown("### Ready for your first demo")
    st.write(
        "Upload a synthetic resume, paste resume text, or choose a sample resume from the sidebar. "
        "The app will extract skills, compare them to the target role dataset, and generate a focused roadmap."
    )
    st.markdown("</div>", unsafe_allow_html=True)