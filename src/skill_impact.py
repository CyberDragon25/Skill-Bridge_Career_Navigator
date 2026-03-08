from typing import List, Dict
from src.gap_analyzer import analyze_gap_for_role


def simulate_skill_impact(
    current_skills: List[str],
    jobs: List[Dict],
    role: str,
    candidate_missing_skills: List[Dict]
) -> List[Dict]:
    """
    For each missing skill, simulate adding it and recompute match score.
    """
    baseline = analyze_gap_for_role(current_skills, jobs, role)
    baseline_score = baseline["match_percentage"]

    impacts = []

    for item in candidate_missing_skills:
        skill = item["skill"]
        updated_skills = list(set(current_skills + [skill]))
        updated_result = analyze_gap_for_role(updated_skills, jobs, role)
        new_score = updated_result["match_percentage"]

        impacts.append({
            "skill": skill,
            "current_score": baseline_score,
            "new_score": new_score,
            "score_gain": round(new_score - baseline_score, 1),
            "appears_in_jobs": item.get("appears_in_jobs", 0),
            "priority": item.get("priority", "Medium")
        })

    impacts.sort(key=lambda x: (-x["score_gain"], -x["appears_in_jobs"], x["skill"]))
    return impacts