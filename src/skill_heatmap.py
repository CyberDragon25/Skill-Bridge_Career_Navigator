from collections import defaultdict
from typing import List, Dict
import pandas as pd


def build_skill_demand_matrix(jobs: List[Dict]) -> pd.DataFrame:
    """
    Build a role x skill matrix where values represent
    how many job postings mention each skill.
    """
    role_skill_counts = defaultdict(lambda: defaultdict(int))

    for job in jobs:
        role = job.get("role", "Unknown")
        required = job.get("required_skills", [])
        nice = job.get("nice_to_have_skills", [])

        for skill in required:
            role_skill_counts[role][skill] += 1

        for skill in nice:
            role_skill_counts[role][skill] += 1

    df = pd.DataFrame(role_skill_counts).fillna(0).astype(int)
    df.index.name = "Skill"
    return df


def get_top_skills_for_role(jobs: List[Dict], role: str, top_n: int = 10) -> pd.DataFrame:
    """
    Return top skills for a specific role, sorted by frequency.
    """
    df = build_skill_demand_matrix(jobs)

    if role not in df.columns:
        return pd.DataFrame(columns=["Skill", "Demand"])

    role_df = df[[role]].reset_index()
    role_df.columns = ["Skill", "Demand"]
    role_df = role_df.sort_values(by="Demand", ascending=False)
    role_df = role_df[role_df["Demand"] > 0].head(top_n)

    return role_df


def get_most_transferable_skills(jobs: List[Dict], top_n: int = 10) -> pd.DataFrame:
    """
    Skills that appear across the greatest number of roles.
    """
    df = build_skill_demand_matrix(jobs)

    transferable = []
    for skill in df.index:
        non_zero_roles = (df.loc[skill] > 0).sum()
        total_mentions = df.loc[skill].sum()

        transferable.append({
            "Skill": skill,
            "Roles Mentioned In": int(non_zero_roles),
            "Total Mentions": int(total_mentions),
        })

    out = pd.DataFrame(transferable)
    out = out.sort_values(
        by=["Roles Mentioned In", "Total Mentions"],
        ascending=[False, False]
    ).head(top_n)

    return out