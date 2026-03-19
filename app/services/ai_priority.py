"""
AI 기반 태스크 우선순위 제안 서비스
"""
import json
import google.generativeai as genai
from typing import List
from app.config import config


class AIPriorityService:
    def __init__(self):
        genai.configure(api_key=config.GEMINI_API_KEY)
        self.model = genai.GenerativeModel("gemini-1.5-flash")

    async def suggest_priorities(self, tasks: List[dict]) -> List[dict]:
        """태스크 목록의 우선순위 자동 제안"""
        if not tasks:
            return []

        task_list = "\n".join([
            f"- ID:{t['id']} 제목:{t['title']} 마감:{t.get('due_date', '없음')} 현재우선순위:{t.get('priority', 'medium')}"
            for t in tasks[:20]
        ])

        prompt = f"""다음 태스크 목록의 우선순위를 분석해줘.

태스크 목록:
{task_list}

각 태스크에 대해 우선순위(high/medium/low)와 이유를 제안해줘.
마감일이 가까울수록, 중요도가 높을수록 high.

JSON으로 반환:
[{{"id": 1, "suggested_priority": "high", "reason": "마감일 임박"}}]"""

        try:
            response = self.model.generate_content(prompt)
            text = response.text.strip()
            if text.startswith("```"):
                text = text[text.find("["):text.rfind("]") + 1]
            suggestions = json.loads(text)
            return suggestions if isinstance(suggestions, list) else []
        except Exception:
            return []

    async def suggest_task_breakdown(self, task_title: str, task_description: str = "") -> List[str]:
        """복잡한 태스크를 작은 서브태스크로 분해"""
        prompt = f"""다음 태스크를 실행 가능한 서브태스크 3-5개로 분해해줘.

태스크: {task_title}
설명: {task_description or '없음'}

JSON 배열로 반환: ["서브태스크1", "서브태스크2"]
각 서브태스크는 구체적이고 30자 이내."""

        try:
            response = self.model.generate_content(prompt)
            text = response.text.strip()
            if text.startswith("```"):
                text = text[text.find("["):text.rfind("]") + 1]
            subtasks = json.loads(text)
            return subtasks if isinstance(subtasks, list) else []
        except Exception:
            return []


ai_priority_service = AIPriorityService()
