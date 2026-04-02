from app.agents.base import load_skill


def read_skill(skill_path: str) -> str:
    return load_skill(skill_path)
