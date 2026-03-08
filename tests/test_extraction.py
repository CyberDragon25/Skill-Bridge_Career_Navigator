from src.skill_extractor import extract_skills


def test_extract_skills_finds_known_skills_in_fallback_mode():
    text = "Built REST APIs in Python, deployed with Docker, and used AWS on Linux."
    known_skills = ["Python", "Docker", "AWS", "Linux", "React", "REST APIs"]

    result = extract_skills(text, known_skills, use_ai=False)

    assert result["method"] == "fallback"
    assert "Python" in result["skills"]
    assert "Docker" in result["skills"]
    assert "AWS" in result["skills"]
    assert "Linux" in result["skills"]
    assert "REST APIs" in result["skills"]
    assert "React" not in result["skills"]
