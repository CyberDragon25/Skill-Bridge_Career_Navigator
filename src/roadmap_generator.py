import json
import os
from dotenv import load_dotenv

load_dotenv()

DEFAULT_RESOURCES = {
    "AWS": {
        "time": "2 weeks",
        "resource": "Complete an AWS fundamentals course and deploy one simple cloud-hosted app.",
        "url": "https://aws.amazon.com/training/digital/aws-cloud-practitioner-essentials/"
    },
    "Docker": {
        "time": "1 week",
        "resource": "Containerize a small app and practice image creation, running, and debugging.",
        "url": "https://docs.docker.com/get-started/"
    },
    "Terraform": {
        "time": "2 weeks",
        "resource": "Learn infrastructure as code basics and provision one small cloud resource stack.",
        "url": "https://developer.hashicorp.com/terraform/tutorials"
    },
    "Kubernetes": {
        "time": "2 weeks",
        "resource": "Deploy a sample containerized app to a local or managed Kubernetes cluster.",
        "url": "https://kubernetes.io/docs/tutorials/"
    },
    "CI/CD": {
        "time": "1 week",
        "resource": "Build one CI/CD pipeline using GitHub Actions or Jenkins for a sample project.",
        "url": "https://docs.github.com/en/actions"
    },
    "Linux": {
        "time": "1 week",
        "resource": "Practice shell navigation, file permissions, process management, and scripting basics.",
        "url": "https://linuxjourney.com/"
    },
    "SQL": {
        "time": "1 week",
        "resource": "Write queries for filtering, joins, aggregation, and basic analytics tasks.",
        "url": "https://www.w3schools.com/sql/"
    }
}

def _generate_roadmap_ai(missing_skills: list[dict], role: str) -> list[dict]:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("Missing OPENAI_API_KEY")

    from openai import OpenAI
    client = OpenAI(api_key=api_key)

    prompt = f"""
You are generating a concise technical upskilling roadmap.

Return ONLY valid JSON in this format:
{{
  "roadmap": [
    {{
      "skill": "AWS",
      "why_it_matters": "Appears frequently in the target role dataset.",
      "time": "2 weeks",
      "resource": "Complete AWS fundamentals and deploy a sample app.",
      "url": "https://example.com"
    }}
  ]
}}

Target role: {role}
Missing skills:
{missing_skills}

Rules:
- Keep roadmap to top 3 skills.
- Make the guidance practical and concrete.
- Use realistic time estimates.
- Prefer free or official resources when possible.
"""

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": "You produce strict JSON only."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.2
    )

    content = response.choices[0].message.content.strip()
    parsed = json.loads(content)
    return parsed.get("roadmap", [])

def generate_roadmap(missing_skills: list[dict], role: str, use_ai: bool = True) -> dict:
    if not missing_skills:
        return {"roadmap": [], "estimated_total_time": "0 weeks"}

    top_missing = missing_skills[:3]

    if use_ai:
        try:
            roadmap = _generate_roadmap_ai(top_missing, role)
            if roadmap:
                total_weeks = 0
                for item in roadmap:
                    try:
                        total_weeks += int(item["time"].split()[0])
                    except Exception:
                        total_weeks += 2
                return {
                    "roadmap": roadmap,
                    "estimated_total_time": f"{total_weeks} weeks"
                }
        except Exception:
            pass

    roadmap = []
    total_weeks = 0

    for item in top_missing:
        skill = item["skill"]
        freq = item.get("appears_in_jobs", 1)
        resource_info = DEFAULT_RESOURCES.get(skill, {
            "time": "2 weeks",
            "resource": f"Complete a guided project and one learning resource for {skill}.",
            "url": f"https://www.google.com/search?q={skill.replace(' ', '+')}+official+tutorial"
        })

        roadmap.append({
            "skill": skill,
            "why_it_matters": f"{skill} appears in {freq} role-specific job postings in this dataset.",
            "time": resource_info["time"],
            "resource": resource_info["resource"],
            "url": resource_info["url"]
        })

        try:
            total_weeks += int(resource_info["time"].split()[0])
        except Exception:
            total_weeks += 2

    return {
        "roadmap": roadmap,
        "estimated_total_time": f"{total_weeks} weeks"
    }