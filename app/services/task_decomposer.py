import google.generativeai as genai
from app.config import config

genai.configure(api_key=config.GEMINI_API_KEY)


async def decompose_project(title: str, description: str, deadline_days: int) -> list[dict]:
    """프로젝트를 작업으로 분해"""
    model = genai.GenerativeModel("gemini-1.5-flash")
    prompt = f"""프로젝트: {title}
설명: {description}
기간: {deadline_days}일

이 프로젝트를 실행 가능한 작업으로 분해하세요. JSON 형식:
{{"tasks": [{{"title": "작업명", "description": "설명", "priority": "high|medium|low", "estimated_days": 2, "skills_needed": ["Python", "React"]}}]}}
한국어로 5-10개 작업 생성."""
    response = model.generate_content(prompt)
    import json, re
    match = re.search(r'\{.*\}', response.text, re.DOTALL)
    return json.loads(match.group())["tasks"] if match else []
