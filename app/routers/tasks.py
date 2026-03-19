from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel
from app.database import get_db
from app.models.task import Task, TaskStatus, TaskPriority
from app.models.project import Project
from app.utils.auth import get_current_user
from app.models.user import User
from app.services.assigner import recommend_assignee

router = APIRouter(prefix="/api/tasks", tags=["tasks"])


class TaskCreate(BaseModel):
    project_id: int
    title: str
    description: Optional[str] = None
    priority: Optional[TaskPriority] = TaskPriority.medium
    due_date: Optional[datetime] = None
    skills_needed: Optional[List[str]] = []
    estimated_days: Optional[int] = 1


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None
    assignee_id: Optional[int] = None
    due_date: Optional[datetime] = None


class TaskResponse(BaseModel):
    id: int
    project_id: int
    title: str
    description: Optional[str]
    assignee_id: Optional[int]
    status: str
    priority: str
    skills_needed: Optional[List[str]]
    estimated_days: int
    due_date: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


@router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    data: TaskCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Project).where(Project.id == data.project_id, Project.owner_id == current_user.id))
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Project not found")

    task = Task(**data.dict())
    db.add(task)
    await db.commit()
    await db.refresh(task)
    return task


@router.get("/project/{project_id}", response_model=List[TaskResponse])
async def list_tasks(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Project).where(Project.id == project_id, Project.owner_id == current_user.id))
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Project not found")

    tasks = await db.execute(select(Task).where(Task.project_id == project_id))
    return tasks.scalars().all()


@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: int,
    data: TaskUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Task).where(Task.id == task_id))
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    proj = await db.execute(select(Project).where(Project.id == task.project_id, Project.owner_id == current_user.id))
    if not proj.scalar_one_or_none():
        raise HTTPException(status_code=403, detail="Not authorized")

    for field, value in data.dict(exclude_none=True).items():
        setattr(task, field, value)
    await db.commit()
    await db.refresh(task)
    return task


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Task).where(Task.id == task_id))
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    proj = await db.execute(select(Project).where(Project.id == task.project_id, Project.owner_id == current_user.id))
    if not proj.scalar_one_or_none():
        raise HTTPException(status_code=403, detail="Not authorized")

    await db.delete(task)
    await db.commit()


@router.post("/{task_id}/assign")
async def auto_assign(
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """팀원 스킬 기반 작업 자동 배분 추천"""
    result = await db.execute(select(Task).where(Task.id == task_id))
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    users_result = await db.execute(select(User).where(User.is_active == True))
    team_members = users_result.scalars().all()

    recommendation = await recommend_assignee(task, team_members)
    return recommendation
