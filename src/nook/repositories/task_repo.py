
from sqlalchemy.orm import Session
from sqlalchemy import select

from nook.models.task import Task
from typing_extensions import overload, override

class TaskRepository:
    def __init__(self,db: Session):
        self.db = db

    def create_task(
        self,
        title: str,
        scope_path: str,
        description: str | None = None,
    ) -> Task:
        """Create a task."""
        try:
            task = Task(
                title= title,
                description= description,
                scope_path= scope_path
            )
    
            self.db.add(task)
            self.db.commit()
            self.db.refresh(task)
    
            return task
        except Exception:
            self.db.rollback()
            raise
    def get_task(self, task_id: int) -> Task | None:
        """Retrieve a task by its ID."""
            
        statement = select(Task).where(Task.id == task_id)
            
        return self.db.scalar(statement)

        
    def get_tasks(
        self,
        scope_path: str,
        recursive: bool = False
    ) -> list[Task]:
        """Retrieve tasks from the current folder or entire project."""
    
        statement = select(Task)
    
        if not recursive:
            statement = statement.where(Task.scope_path == scope_path)
    
        statement = statement.order_by(Task.id)
    
        return list(self.db.scalars(statement).all())
        

    def update_task(
        self,
        task_id: int,
        title: str | None = None,
        description: str | None = None
    ) -> Task | None:
        """Update an existing task."""

        task = self.get_task(task_id=task_id)

        if task is None:
            return None

        try:
            if title is not None:
                task.title = title

            if description is not None:
                task.description = description

            self.db.commit()
            self.db.refresh(task)

            return task
        except Exception:
            self.db.rollback()
            raise

    def complete_task(self,task_id: int) -> Task | None:
        """Mark an existing task as completed."""

        task = self.get_task(task_id=task_id)

        if task is None:
            return None

        try:
            task.status = "completed"
            self.db.commit()
            self.db.refresh(task)
            return task
        except Exception:
            self.db.rollback()
            raise
            
    
    def complete_task_by_title(
         self,
         title: str,
         scope_path: str
     ) -> Task | None:
         """Find and complete a task by its title."""
         statement = select(Task).where(
             Task.title == title,
             Task.scope_path == scope_path,
             Task.status != "completed"
         )

         task = self.db.scalar(statement)

         if task is None:
             return None
             
         try:
             task.status = "completed"
             self.db.commit()
             self.db.refresh(task)
             return task
         except Exception:
             self.db.rollback()
             raise


    def delete_task(self,task_id: int) -> bool:
        """Delete a task by its ID."""

        task = self.get_task(task_id=task_id)

        if task is None:
            return False

        try:
            self.db.delete(task)
            self.db.commit()
            return True
        except Exception:
            self.db.rollback()
            raise

    def get_tasks_by_title(
        self,
        title: str,
        scope_path: str
    ) -> list[Task]:
        """Find all tasks matching a title within a scope."""

        statement = (select(Task)
                    .where(
                        Task.title== title,
                        Task.scope_path== scope_path,
                    )
                    .order_by(Task.id)
        )

        return list(self.db.scalars(statement).all())

    def delete_all_tasks(
        self,
        scope_path: str,
        recursive: bool = False
    ) -> int:
        """Delete all tasks in the current scope or entire project."""
    
        try:
            statement = select(Task)
    
            if not recursive:
                statement = statement.where(Task.scope_path == scope_path)
    
            tasks = self.db.scalars(statement).all()
            count = len(tasks)
    
            for task in tasks:
                self.db.delete(task)
    
            self.db.commit()
    
            return count
    
        except Exception:
            self.db.rollback()
            raise