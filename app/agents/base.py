import json
import logging
from pathlib import Path

from openai import AsyncOpenAI

from app.core.config import settings

logger = logging.getLogger(__name__)

SKILLS_DIR = Path(__file__).parent / "skills"


def get_llm_client() -> AsyncOpenAI:
    return AsyncOpenAI(
        base_url=settings.llm_api_url,
        api_key=settings.llm_api_key or "not-needed",
    )


async def run_agent(
    name: str,
    system_prompt: str,
    user_message: str,
    tools: list[dict] | None = None,
    tool_handlers: dict | None = None,
) -> dict:
    client = get_llm_client()
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_message},
    ]

    max_iterations = 10
    for _ in range(max_iterations):
        kwargs = {"model": settings.llm_model_name, "messages": messages}
        if tools:
            kwargs["tools"] = tools

        response = await client.chat.completions.create(**kwargs)
        choice = response.choices[0]

        if choice.finish_reason == "tool_calls" and choice.message.tool_calls:
            messages.append(choice.message)
            for tool_call in choice.message.tool_calls:
                fn_name = tool_call.function.name
                fn_args = json.loads(tool_call.function.arguments)
                handler = tool_handlers.get(fn_name) if tool_handlers else None
                if handler:
                    try:
                        result = await handler(**fn_args)
                        if isinstance(result, (dict, list)):
                            result_str = json.dumps(result)
                        else:
                            result_str = str(result)
                    except Exception as e:
                        result_str = f"Error: {e}"
                else:
                    result_str = f"Unknown tool: {fn_name}"
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": result_str,
                })
            continue

        content = choice.message.content or ""
        try:
            if "```json" in content:
                json_str = content.split("```json")[1].split("```")[0].strip()
            elif "{" in content:
                start = content.index("{")
                end = content.rindex("}") + 1
                json_str = content[start:end]
            else:
                json_str = content
            return json.loads(json_str)
        except (json.JSONDecodeError, ValueError):
            logger.warning(f"Agent {name} returned non-JSON: {content[:200]}")
            return {"raw_response": content}

    logger.error(f"Agent {name} hit max iterations")
    return {"error": "max iterations reached"}


def load_skill(skill_path: str) -> str:
    full_path = SKILLS_DIR / skill_path
    if full_path.exists():
        return full_path.read_text(encoding="utf-8")
    return f"Skill not found: {skill_path}"
