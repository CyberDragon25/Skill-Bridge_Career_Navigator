import streamlit as st
import pandas as pd

from src.data_loader import load_jobs, load_skills, load_sample_resume, get_available_roles
from src.validators import validate_resume_text, validate_role
from src.skill_extractor import extract_skills, merge_text_sources
from src.gap_analyzer import analyze_gap_for_role
from src.roadmap_generator import generate_roadmap
from src.pdf_parser import extract_text_from_pdf_bytes
from src.role_classifier import predict_role_fit
from src.skill_impact import simulate_skill_impact

from src.skill_heatmap import (
    build_skill_demand_matrix,
    get_top_skills_for_role,
    get_most_transferable_skills,
)


jobs = load_jobs()
skills = load_skills()
roles = get_available_roles(jobs)


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


st.set_page_config(
    page_title="SkillBridge Career Navigator",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded",
)

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
    </style>
    """,
    unsafe_allow_html=True,
)

with st.sidebar:
    st.markdown("## 🚀 SkillBridge")
    st.caption("AI + ML assisted career navigation demo")

    target_role = st.selectbox("Target role", roles)
    use_ai = st.toggle("Use AI where available", value=True)
    show_job_explorer = st.toggle("Show job explorer", value=True)
    show_skill_heatmap = st.toggle("Show skill demand heatmap", value=True) # skill heatmap

    sample_resume_option = st.selectbox(
        "Sample resume",
        ["None", "sample_resume1.txt", "sample_resume2.txt", "sample_resume3.txt"],
        index=0,
    )

    st.markdown("---")
    st.markdown("### Demo flow")
    st.markdown("1. Upload resume or PDF")
    st.markdown("2. Pick a role")
    st.markdown("3. Compare AI + ML outputs")
    st.markdown("4. Review roadmap and skill impact")

role_jobs = [job for job in jobs if job["role"] == target_role]
primary_job = role_jobs[0] if role_jobs else {
    "title": target_role,
    "description": "",
    "required_skills": [],
    "nice_to_have_skills": []
}

st.markdown(
    f"""
    <div class="hero-card">
        <div class="section-kicker">AI-assisted career planning</div>
        <h1 style="margin:.35rem 0 .6rem 0;">SkillBridge Career Navigator</h1>
        <p style="font-size:1.05rem; color:#cbd5e1; max-width:760px; margin:0;">
            Extract skills from resumes and supplemental documents, estimate likely role fit with a lightweight ML model,
            and generate an explainable roadmap for <b>{target_role}</b>.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

left, right = st.columns([1.15, 0.85], gap="large")

resume_text = ""
supplemental_text = ""

with left:
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.markdown("### 📄 Candidate Input")

    uploaded_resume = st.file_uploader(
        "Upload resume (.txt, .md, or .pdf)",
        type=["txt", "md", "pdf"],
        key="resume_upload",
    )

    uploaded_analysis_pdf = st.file_uploader(
        "Upload supplemental analysis / portfolio PDF (optional)",
        type=["pdf"],
        key="analysis_pdf_upload",
    )

    if uploaded_resume is not None:
        if uploaded_resume.name.lower().endswith(".pdf"):
            resume_text = extract_text_from_pdf_bytes(uploaded_resume.getvalue())
        else:
            try:
                resume_text = uploaded_resume.read().decode("utf-8", errors="ignore")
            except Exception:
                resume_text = ""

    if uploaded_analysis_pdf is not None:
        supplemental_text = extract_text_from_pdf_bytes(uploaded_analysis_pdf.getvalue())

    if sample_resume_option != "None" and not resume_text.strip():
        try:
            resume_text = load_sample_resume(sample_resume_option)
        except Exception:
            resume_text = ""

    pasted_resume = st.text_area(
        "Or paste resume text",
        value=resume_text,
        height=220,
        placeholder="Paste synthetic resume content here...",
    )

    if pasted_resume.strip():
        resume_text = pasted_resume

    combined_text = merge_text_sources(resume_text, supplemental_text)

    analyze_clicked = st.button("Analyze my fit", type="primary", use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

with right:
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.markdown("### 🎯 Role Snapshot")
    st.markdown(f"**{primary_job.get('title', target_role)}**")
    st.caption(primary_job.get("description", ""))

    st.markdown("**Required skills**")
    st.markdown(badge_list(primary_job.get("required_skills", []), "neutral"), unsafe_allow_html=True)

    st.markdown("**Nice to have**")
    st.markdown(badge_list(primary_job.get("nice_to_have_skills", []), "nice"), unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

if analyze_clicked:
    try:
        validate_resume_text(combined_text)
        validate_role(target_role, jobs)

        with st.spinner("Running AI + ML analysis..."):
            extraction_result = extract_skills(
                text=combined_text,
                known_skills=skills,
                use_ai=use_ai
            )

            extracted_skills = extraction_result["skills"]

            role_prediction = predict_role_fit(
                resume_text=combined_text,
                jobs=jobs
            )

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

            impact_result = simulate_skill_impact(
                current_skills=extracted_skills,
                jobs=jobs,
                role=target_role,
                candidate_missing_skills=gap_result["missing_skills"]
            )

        st.session_state["analysis"] = {
            "skills": extracted_skills,
            "result": gap_result,
            "roadmap": roadmap_result,
            "role_prediction": role_prediction,
            "impact_result": impact_result,
            "extraction_method": extraction_result["method"],
            "confidence": extraction_result["confidence"],
            "supplemental_used": bool(supplemental_text.strip()),
        }

    except ValueError as e:
        st.error(str(e))
    except Exception as e:
        st.error(f"Unexpected error: {e}")

if "analysis" in st.session_state:
    analysis = st.session_state["analysis"]
    extracted = analysis["skills"]
    result = analysis["result"]
    roadmap = analysis["roadmap"]
    role_prediction = analysis["role_prediction"]
    impact_result = analysis["impact_result"]

    extraction_method = analysis.get("extraction_method", "fallback")
    confidence = analysis.get("confidence", "medium")
    supplemental_used = analysis.get("supplemental_used", False)

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
    st.caption(
        f"Skill extraction: {extraction_method.upper()} · Confidence: {confidence.capitalize()} · "
        f"Supplemental PDF used: {'Yes' if supplemental_used else 'No'}"
    )

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

    st.markdown("### 🤖 AI + ML Signals")
    m1, m2 = st.columns(2)
    with m1:
        st.metric("Predicted best-fit role (ML)", role_prediction["predicted_role"])
    with m2:
        st.metric("ML confidence", f"{role_prediction['confidence']}%")

    if role_prediction["top_roles"]:
        st.dataframe(pd.DataFrame(role_prediction["top_roles"]), use_container_width=True, hide_index=True)

    st.info(
        "AI suggestions may be imperfect. ML role fit is based on the synthetic job dataset, not real hiring outcomes."
    )

    edited_skills = st.multiselect(
        "Review / edit extracted skills",
        options=skills,
        default=extracted,
    )

    if st.button("Re-run analysis with edited skills", use_container_width=True):
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
        impact_result = simulate_skill_impact(
            current_skills=edited_skills,
            jobs=jobs,
            role=target_role,
            candidate_missing_skills=gap_result["missing_skills"]
        )

        st.session_state["analysis"]["skills"] = edited_skills
        st.session_state["analysis"]["result"] = gap_result
        st.session_state["analysis"]["roadmap"] = roadmap_result
        st.session_state["analysis"]["impact_result"] = impact_result
        st.session_state["analysis"]["extraction_method"] = "manual-review"
        st.session_state["analysis"]["confidence"] = "high"
        st.rerun()

    a, b = st.columns([1, 1], gap="large")

    with a:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.markdown("### ✅ Skills Overview")
        st.markdown("**Detected from input**")
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
        st.dataframe(pd.DataFrame(result["missing_skills"]), use_container_width=True, hide_index=True)

    st.markdown("### 📈 Skill Impact Simulator")
    if impact_result:
        best_skill = impact_result[0]
        st.success(
            f"Highest-impact next skill: {best_skill['skill']} "
            f"(match score +{best_skill['score_gain']} points)"
        )

        impact_df = pd.DataFrame(impact_result)
        st.dataframe(impact_df, use_container_width=True, hide_index=True)

        chart_df = impact_df[["skill", "score_gain"]].copy().set_index("skill")
        st.bar_chart(chart_df)
    else:
        st.success("No missing skills left to simulate.")

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

        if show_skill_heatmap:
            st.markdown("### 🔥 Skill Demand Heatmap")

            heatmap_df = build_skill_demand_matrix(jobs)

            if not heatmap_df.empty:
                st.caption(
                    "This view shows how frequently each skill appears across roles in the synthetic job dataset."
                )

                st.info(
                    "These demand patterns come from the synthetic job dataset and are intended to guide role alignment, not predict real hiring outcomes."
                )

                st.dataframe(heatmap_df, use_container_width=True)

                heatmap_chart_df = heatmap_df.copy()
                st.markdown("#### Top skill demand patterns by role")
                st.bar_chart(heatmap_chart_df)

                st.markdown(f"### Top Skills for {target_role}")
                top_role_skills = get_top_skills_for_role(jobs, target_role, top_n=10)

                if not top_role_skills.empty:
                    st.dataframe(top_role_skills, use_container_width=True, hide_index=True)

                    role_chart_df = top_role_skills.set_index("Skill")
                    st.bar_chart(role_chart_df)
                else:
                    st.info("No skill demand data available for this role.")

                st.markdown("### Most Transferable Skills Across Roles")
                transferable_df = get_most_transferable_skills(jobs, top_n=10)

                if not transferable_df.empty:
                    st.dataframe(transferable_df, use_container_width=True, hide_index=True)

                    transferable_chart_df = transferable_df.set_index("Skill")[["Roles Mentioned In"]]
                    st.bar_chart(transferable_chart_df)
                else:
                    st.info("No transferable skill data available.")
            else:
                st.info("Skill demand matrix could not be built from the current dataset.")

        if show_job_explorer:
            st.markdown("### 🧾 Job Explorer")
            if role_jobs:
                st.dataframe(pd.DataFrame(role_jobs), use_container_width=True, hide_index=True)
            else:
                st.info("No jobs found for this role in the current dataset.")
else:
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.markdown("### Ready for your first demo")
    st.write(
        "Upload a synthetic resume or PDF, optionally add a supplemental analysis PDF, choose a role, and run analysis."
    )
    st.markdown("</div>", unsafe_allow_html=True)