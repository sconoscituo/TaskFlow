import google.generativeai as genai
import json
import re
from app.config import config

genai.configure(api_key=config.GEMINI_API_KEY)


async def recommend_assignee(task, team_members: list) -> dict:
    """Gemini AI로 팀원 스킬 기반 작업 배분 추천"""
    if not team_members:
        return {"message": "No team members available", "recommendation": None}

    members_info = [
        {"id": m.id, "name": m.full_name or m.email, "skills": m.skills or ""}
        for m in team_members
    ]

    model = genai.GenerativeModel("gemini-1.5-flash")
    prompt = f"""작업 정보:
- 제목: {task.title}
- 설명: {task.description or "없음"}
- 필요 스킬: {task.skills_needed or []}
- 우선순위: {task.priority}

팀원 목록:
{json.dumps(members_info, ensure_ascii=False, indent=2)}

가장 적합한 팀원을 추천하고 이유를 설명하세요. JSON 형식:
{{"recommended_id": 1, "recommended_name": "이름", "reason": "추천 이유", "skill_match_score": 85}}"""

    response = model.generate_content(prompt)
    match = re.search(r'\{.*\}', response.text, re.DOTALL)
    if match:
        result = json.loads(match.group())
        return {
            "task_id": task.id,
            "task_title": task.title,
            "recommendation": result
        }
    return {"task_id": task.id, "task_title": task.title, "recommendation": None, "message": "Could not generate recommendation"}
