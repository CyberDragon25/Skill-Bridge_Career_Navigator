from src.gap_analyzer import analyze_gap

def test_gap_analysis_identifies_missing_skills():
    resume_skills = ["Python", "Docker", "Linux"]
    required_skills = ["Python", "AWS", "Docker", "Linux"]
    nice_to_have = ["Terraform"]

    result = analyze_gap(resume_skills, required_skills, nice_to_have)

    assert "AWS" in result["missing_skills"]
    assert "Python" in result["matching_skills"]
    assert result["match_percentage"] == 75.0

    def test_gap_analysis_handles_empty_required_skills():
        result = analyze_gap(["Python"], [], [])
        assert result["match_percentage"] == 0
        assert result["missing_skills"] == []