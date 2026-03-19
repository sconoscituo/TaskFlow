from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel
from app.database import get_db
from app.models.project import Project, ProjectStatus
from app.models.task import Task, TaskPriority, TaskStatus
from app.utils.auth import get_current_user
from app.models.user import User
from app.services.task_decomposer import decompose_project

router = APIRouter(prefix="/api/projects", tags=["projects"])


class ProjectCreate(BaseModel):
    title: str
    description: Optional[str] = None
    deadline: Optional[datetime] = None


class ProjectUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[ProjectStatus] = None
    deadline: Optional[datetime] = None


class ProjectResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    owner_id: int
    status: str
    deadline: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


@router.post("/", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    data: ProjectCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    project = Project(
        title=data.title,
        description=data.description,
        owner_id=current_user.id,
        deadline=data.deadline,
    )
    db.add(project)
    await db.commit()
    await db.refresh(project)
    return project


@router.get("/", response_model=List[ProjectResponse])
async def list_projects(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Project).where(Project.owner_id == current_user.id))
    return result.scalars().all()


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Project).where(Project.id == project_id, Project.owner_id == current_user.id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: int,
    data: ProjectUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Project).where(Project.id == project_id, Project.owner_id == current_user.id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    for field, value in data.dict(exclude_none=True).items():
        setattr(project, field, value)
    await db.commit()
    await db.refresh(project)
    return project


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Project).where(Project.id == project_id, Project.owner_id == current_user.id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    await db.delete(project)
    await db.commit()


@router.post("/{project_id}/decompose")
async def decompose(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """AI로 프로젝트를 작업으로 자동 분해"""
    result = await db.execute(select(Project).where(Project.id == project_id, Project.owner_id == current_user.id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    deadline_days = 30
    if project.deadline:
        delta = project.deadline - datetime.utcnow()
        deadline_days = max(1, delta.days)

    tasks_data = await decompose_project(project.title, project.description or "", deadline_days)

    created_tasks = []
    for t in tasks_data:
        task = Task(
            project_id=project.id,
            title=t.get("title", "Untitled Task"),
            description=t.get("description", ""),
            priority=t.get("priority", TaskPriority.medium),
            skills_needed=t.get("skills_needed", []),
            estimated_days=t.get("estimated_days", 1),
        )
        db.add(task)
        created_tasks.append(task)

    await db.commit()
    return {"message": f"{len(created_tasks)} tasks created", "tasks": [{"title": t.title, "priority": t.priority} for t in created_tasks]}


@router.get("/{project_id}/bottleneck")
async def detect_bottleneck(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """AI 병목 감지 및 해결책 제안"""
    result = await db.execute(select(Project).where(Project.id == project_id, Project.owner_id == current_user.id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    tasks_result = await db.execute(select(Task).where(Task.project_id == project_id))
    tasks = tasks_result.scalars().all()

    blocked = [t for t in tasks if t.status == TaskStatus.blocked]
    in_progress = [t for t in tasks if t.status == TaskStatus.in_progress]
    total = len(tasks)
    done = len([t for t in tasks if t.status == TaskStatus.done])

    bottlenecks = []
    suggestions = []

    if blocked:
        bottlenecks.append(f"{len(blocked)} blocked tasks detected")
        suggestions.append("Review and resolve blocking dependencies immediately")

    if total > 0 and done / total < 0.3 and project.deadline:
        delta = project.deadline - datetime.utcnow()
        if delta.days < 7:
            bottlenecks.append("Project deadline approaching with low completion rate")
            suggestions.append("Consider reducing scope or adding resources")

    unassigned = [t for t in tasks if not t.assignee_id and t.status == TaskStatus.todo]
    if unassigned:
        bottlenecks.append(f"{len(unassigned)} tasks are unassigned")
        suggestions.append("Use /assign endpoint to auto-assign tasks based on skills")

    return {
        "project_id": project_id,
        "progress": f"{done}/{total} tasks completed",
        "bottlenecks": bottlenecks,
        "suggestions": suggestions,
    }
