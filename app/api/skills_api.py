import re

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.base import SKILLS_DIR
from app.core.database import get_session
from app.models import SkillVersion, SkillVersionSchema

router = APIRouter(tags=["skills"])


def _parse_frontmatter(content: str) -> dict:
    """Extract name and description from SKILL.md frontmatter."""
    result = {"name": "", "description": ""}
    fm_match = re.match(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
    if fm_match:
        for line in fm_match.group(1).splitlines():
            if line.startswith("name:"):
                result["name"] = line.split(":", 1)[1].strip().strip('"').strip("'")
            elif line.startswith("description:"):
                result["description"] = line.split(":", 1)[1].strip().strip('"').strip("'")
    # Fallback: use first heading as name
    if not result["name"]:
        heading = re.search(r"^#\s+(.+)", content, re.MULTILINE)
        if heading:
            result["name"] = heading.group(1).strip()
    return result


@router.get("/api/skills")
async def list_skills():
    skills = []
    if not SKILLS_DIR.exists():
        return skills
    for md_file in sorted(SKILLS_DIR.rglob("*.md")):
        rel_path = md_file.relative_to(SKILLS_DIR).as_posix()
        content = md_file.read_text(encoding="utf-8")
        meta = _parse_frontmatter(content)
        skills.append({
            "path": rel_path,
            "name": meta["name"] or rel_path,
            "description": meta["description"],
        })
    return skills


@router.get("/api/skills/{skill_path:path}")
async def get_skill(skill_path: str):
    full_path = SKILLS_DIR / skill_path
    if not full_path.exists() or not full_path.is_file():
        raise HTTPException(status_code=404, detail="Skill not found")
    content = full_path.read_text(encoding="utf-8")
    meta = _parse_frontmatter(content)
    return {
        "path": skill_path,
        "name": meta["name"] or skill_path,
        "description": meta["description"],
        "content": content,
    }


@router.get("/api/skills/{skill_path:path}/versions", response_model=list[SkillVersionSchema])
async def list_skill_versions(
    skill_path: str,
    session: AsyncSession = Depends(get_session),
):
    result = await session.execute(
        select(SkillVersion)
        .where(SkillVersion.skill_path == skill_path)
        .order_by(SkillVersion.version.desc())
    )
    return result.scalars().all()
