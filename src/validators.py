def validate_resume_text(text: str):
    if not text or len(text.strip()) < 20:
        raise ValueError("Please upload or paste a longer synthetic resume before analysis.")

def validate_role(role: str, jobs: list):
    valid_roles = {job["role"] for job in jobs}
    if role not in valid_roles:
        raise ValueError(f"Unsupported role selected: {role}")