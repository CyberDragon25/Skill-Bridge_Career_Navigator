from collections import Counter

def analyze_gap_for_role(candidate_skills: list[str], jobs: list[dict], role: str) -> dict:
    role_jobs = [job for job in jobs if job["role"] == role]

    if not role_jobs:
        return {
            "matching_skills": [],
            "missing_skills": [],
            "matching_nice_to_have": [],
            "extra_skills": candidate_skills,
            "match_percentage": 0,
            "recommendation": "No jobs available for this role in the dataset."
        }

    candidate_set = {s.lower().strip() for s in candidate_skills}

    required_counter = Counter()
    nice_counter = Counter()

    for job in role_jobs:
        required_counter.update(job.get("required_skills", []))
        nice_counter.update(job.get("nice_to_have_skills", []))

    required_skills = list(required_counter.keys())
    nice_to_have_skills = list(nice_counter.keys())

    matching_required = [s for s in required_skills if s.lower() in candidate_set]
    missing_required = []

    for skill in required_skills:
        if skill.lower() not in candidate_set:
            freq = required_counter[skill]
            missing_required.append({
                "skill": skill,
                "appears_in_jobs": freq,
                "priority": "High" if freq >= max(2, len(role_jobs) * 0.6) else "Medium"
            })

    matching_nice = [s for s in nice_to_have_skills if s.lower() in candidate_set]

    required_lower = {s.lower().strip() for s in required_skills}
    nice_lower = {s.lower().strip() for s in nice_to_have_skills}
    extra_skills = [s for s in candidate_skills if s.lower().strip() not in required_lower and s.lower().strip() not in nice_lower]

    total_required_unique = len(required_skills)
    match_pct = round((len(matching_required) / total_required_unique) * 100, 1) if total_required_unique else 0

    if match_pct >= 80:
        recommendation = "Excellent match — you appear ready to apply."
    elif match_pct >= 60:
        recommendation = "Strong baseline — focus on the highest-frequency missing skills first."
    elif match_pct >= 40:
        recommendation = "Moderate fit — a focused upskilling plan should improve competitiveness."
    else:
        recommendation = "Early-stage fit — build a stronger technical baseline before applying broadly."

    missing_required = sorted(
        missing_required,
        key=lambda x: (-x["appears_in_jobs"], x["skill"])
    )

    return {
        "matching_skills": matching_required,
        "missing_skills": missing_required,
        "matching_nice_to_have": matching_nice,
        "extra_skills": extra_skills[:10],
        "match_percentage": match_pct,
        "recommendation": recommendation
    }