from abc import abstractmethod
from typing import Any, Dict, List, Optional
from app.domain.ports.base_service import AbstractService


class AbstractTaskService(AbstractService):
    @abstractmethod
    async def create_task(self, project_id: int, data: Dict[str, Any]) -> Dict[str, Any]: ...
    @abstractmethod
    async def assign_task(self, task_id: int, user_id: int) -> Dict[str, Any]: ...
    @abstractmethod
    async def get_team_tasks(self, project_id: int, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]: ...
    @abstractmethod
    async def track_progress(self, project_id: int) -> Dict[str, Any]: ...
