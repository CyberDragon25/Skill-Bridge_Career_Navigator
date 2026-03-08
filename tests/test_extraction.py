from src.skill_extractor import extract_skills

def test_extract_skills_finds_known_skills():
    text = "Built APIs in Python, deployed with Docker, and used AWS on Linux."
    known_skills = ["Python", "Docker", "AWS", "Linux", "React"]
    result = extract_skills(text, known_skills)
    assert "Python" in result
    assert "Docker" in result
    assert "AWS" in result
    assert "Linux" in result
    assert "React" not in result