from src.gap_analyzer import analyze_gap_for_role


TEST_JOBS = [
    {
        "id": "cloud-001",
        "title": "Junior Cloud Engineer",
        "role": "Cloud Engineer",
        "required_skills": ["AWS", "Linux", "Python", "Docker"],
        "nice_to_have_skills": ["Terraform", "CI/CD"],
    },
    {
        "id": "cloud-002",
        "title": "Cloud Platform Engineer",
        "role": "Cloud Engineer",
        "required_skills": ["AWS", "Linux", "Kubernetes", "CI/CD"],
        "nice_to_have_skills": ["Terraform", "Bash"],
    },
]


def test_gap_analysis_identifies_missing_required_skills():
    candidate_skills = ["Python", "Docker", "Linux"]

    result = analyze_gap_for_role(candidate_skills, TEST_JOBS, "Cloud Engineer")

    assert "Python" in result["matching_skills"]
    assert "Linux" in result["matching_skills"]

    missing_names = [item["skill"] for item in result["missing_skills"]]
    assert "AWS" in missing_names
    assert result["match_percentage"] == 50.0


def test_gap_analysis_handles_missing_role():
    result = analyze_gap_for_role(["Python"], TEST_JOBS, "Data Analyst")

    assert result["match_percentage"] == 0
    assert result["missing_skills"] == []
    assert result["matching_skills"] == []
