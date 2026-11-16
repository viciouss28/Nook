from dataclasses import dataclass
from typing import Literal

from nook.models.task import Task
from nook.repositories.task_repo import TaskRepository


@dataclass
class TaskActionResult:
    identifier: int | str
    status: Literal["completed", "not_found", "ambiguous", "deleted"]
    task: Task | None = None


class TaskService:
    def __init__(self, repository: TaskRepository):
        self.repository = repository

    def complete_tasks_by_ids(
        self,
        task_ids: list[int]
    ) -> list[TaskActionResult]:
        results = []

        for task_id in task_ids:
            task = self.repository.complete_task(task_id)

            if task is None:
                results.append(
                    TaskActionResult(
                        identifier=task_id,
                        status="not_found"
                    )
                )
            else:
                results.append(
                    TaskActionResult(
                        identifier=task_id,
                        status="completed",
                        task=task
                    )
                )

        return results

    def complete_tasks_by_titles(
        self,
        titles: list[str],
        scope_path: str
    ) -> list[TaskActionResult]:
        results = []
    
        for title in titles:
            tasks = self.repository.get_tasks_by_title(
                title=title,
                scope_path=scope_path
            )
    
            if not tasks:
                results.append(
                    TaskActionResult(
                        identifier=title,
                        status="not_found"
                    )
                )
    
            elif len(tasks) > 1:
                results.append(
                    TaskActionResult(
                        identifier=title,
                        status="ambiguous"
                    )
                )
    
            else:
                task = self.repository.complete_task(tasks[0].id)
    
                results.append(
                    TaskActionResult(
                        identifier=title,
                        status="completed" if task else "not_found",
                        task=task
                    )
                )
    
        return results
    def delete_tasks_by_ids(
        self,
        task_ids: list[int]
    ) -> list[TaskActionResult]:
        results = []
        
        for task_id in task_ids:
            
            deleted = self.repository.delete_task(task_id)
            results.append(
                    TaskActionResult(
                        identifier=task_id,
                        status="deleted" if deleted else "not_found"
                    )
                )
        
        return results

        
    def delete_tasks_by_titles(
            self,
            titles: list[str],
            scope_path: str
        ) -> list[TaskActionResult]:
        results = []
        
        for title in titles:
            tasks = self.repository.get_tasks_by_title(
                title=title,
                scope_path=scope_path
        )
        
            if not tasks:
                results.append(
                    TaskActionResult(
                        identifier=title,
                        status="not_found"
                    )
                )
        
            elif len(tasks) > 1:
                results.append(
                    TaskActionResult(
                        identifier=title,
                        status="ambiguous"
                    )
                )
        
            else:
                deleted = self.repository.delete_task(tasks[0].id)
        
                results.append(
                    TaskActionResult(
                        identifier=title,
                        status="deleted" if deleted else "not_found"
                    )
                )
        
        return results