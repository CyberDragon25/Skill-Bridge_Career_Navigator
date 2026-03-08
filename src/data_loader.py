import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

def load_jobs():
    with open(DATA_DIR / "jobs.json", "r", encoding="utf-8") as f:
        return json.load(f)

def load_skills():
    with open(DATA_DIR / "skills.json", "r", encoding="utf-8") as f:
        return json.load(f)

def load_sample_resume(filename: str) -> str:
    with open(DATA_DIR / filename, "r", encoding="utf-8") as f:
        return f.read()

def get_available_roles(jobs):
    return sorted(list({job["role"] for job in jobs}))