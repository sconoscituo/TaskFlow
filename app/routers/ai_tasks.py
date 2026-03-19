"""
AI 태스크 관리 라우터
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from typing import List, Optional
from app.database import get_db
from app.models.user import User
from app.models.task import Task
from app.utils.auth import get_current_user
from app.services.ai_priority import ai_priority_service

router = APIRouter(prefix="/ai", tags=["AI 태스크 관리"])


class BreakdownRequest(BaseModel):
    task_title: str
    task_description: Optional[str] = None


@router.get("/priority-suggestions")
async def get_priority_suggestions(
    project_id: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """현재 태스크들의 AI 우선순위 제안"""
    query = select(Task).where(Task.assignee_id == current_user.id)
    if project_id:
        query = query.where(Task.project_id == project_id)
    result = await db.execute(query.limit(20))
    tasks = result.scalars().all()

    task_dicts = [
        {
            "id": t.id,
            "title": t.title,
            "due_date": str(t.due_date) if hasattr(t, "due_date") and t.due_date else None,
            "priority": str(t.priority) if hasattr(t, "priority") else "medium",
        }
        for t in tasks
    ]

    suggestions = await ai_priority_service.suggest_priorities(task_dicts)
    return {"suggestions": suggestions, "total": len(suggestions)}


@router.post("/breakdown")
async def breakdown_task(
    request: BreakdownRequest,
    current_user: User = Depends(get_current_user),
):
    """복잡한 태스크를 서브태스크로 분해"""
    subtasks = await ai_priority_service.suggest_task_breakdown(
        request.task_title, request.task_description or ""
    )
    return {"subtasks": subtasks, "total": len(subtasks)}
