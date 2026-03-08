import json
import os
import re
from dotenv import load_dotenv

load_dotenv()

SKILL_ALIASES = {
    "Python": ["python"],
    "Java": ["java"],
    "C++": ["c++", "cpp"],
    "JavaScript": ["javascript", "js"],
    "TypeScript": ["typescript", "ts"],
    "React": ["react"],
    "HTML": ["html"],
    "CSS": ["css"],
    "Node.js": ["node.js", "nodejs", "node"],
    "Flask": ["flask"],
    "FastAPI": ["fastapi"],
    "SQL": ["sql", "postgresql", "mysql", "sqlite"],
    "MongoDB": ["mongodb", "mongo"],
    "Docker": ["docker"],
    "Kubernetes": ["kubernetes", "k8s"],
    "AWS": ["aws", "amazon web services"],
    "Azure": ["azure"],
    "GCP": ["gcp", "google cloud"],
    "Terraform": ["terraform"],
    "CI/CD": ["ci/cd", "continuous integration", "continuous delivery", "github actions", "gitlab ci", "jenkins"],
    "Git": ["git", "github"],
    "Linux": ["linux", "ubuntu"],
    "Bash": ["bash", "shell scripting"],
    "REST APIs": ["rest api", "rest apis", "restful api", "api development"],
    "GraphQL": ["graphql"],
    "Microservices": ["microservices", "microservice architecture"],
    "Spark": ["spark", "apache spark"],
    "Kafka": ["kafka", "apache kafka"],
    "Airflow": ["airflow", "apache airflow"],
    "Machine Learning": ["machine learning", "ml"],
    "TensorFlow": ["tensorflow"],
    "PyTorch": ["pytorch"],
    "Ansible": ["ansible"],
    "Snowflake": ["snowflake"],
    "dbt": ["dbt"],
    "MLOps": ["mlops"]
}

def extract_skills_rule_based(text: str, known_skills: list[str]) -> list[str]:
    text_lower = text.lower()
    found = set()

    for skill in known_skills:
        aliases = SKILL_ALIASES.get(skill, [skill.lower()])
        for alias in aliases:
            pattern = r"\b" + re.escape(alias.lower()) + r"\b"
            if re.search(pattern, text_lower):
                found.add(skill)
                break

    return sorted(found)

def _extract_skills_ai(text: str, known_skills: list[str]) -> list[str]:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("Missing OPENAI_API_KEY")

    from openai import OpenAI
    client = OpenAI(api_key=api_key)

    prompt = f"""
You are extracting technical skills from a synthetic resume.

Return ONLY valid JSON in this format:
{{"skills": ["Python", "SQL"]}}

Rules:
- Only include skills from this allowed list.
- Do not invent skills.
- Prefer explicit skills.
- Include commonly implied technical skills only when strongly supported.
- Ignore soft skills.

Allowed skills:
{known_skills}

Resume:
{text}
"""

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": "You extract technical skills into strict JSON."},
            {"role": "user", "content": prompt}
        ],
        temperature=0
    )

    content = response.choices[0].message.content.strip()
    parsed = json.loads(content)

    valid = [skill for skill in parsed.get("skills", []) if skill in known_skills]
    return sorted(list(set(valid)))

def extract_skills(text: str, known_skills: list[str], use_ai: bool = True) -> dict:
    if use_ai:
        try:
            skills = _extract_skills_ai(text, known_skills)
            if skills:
                return {
                    "skills": skills,
                    "method": "ai",
                    "confidence": "high"
                }
        except Exception:
            pass

    skills = extract_skills_rule_based(text, known_skills)
    return {
        "skills": skills,
        "method": "fallback",
        "confidence": "medium" if skills else "low"
    }

def merge_text_sources(*texts: str) -> str:
    parts = [t.strip() for t in texts if t and t.strip()]
    return "\n\n".join(parts)