# Task Queue Manager
# Handles persistent task queue with JSON format
# Supports sequential and parallel task processing

import json
from pathlib import Path

QUEUE_FILE = "task_queue.json"
COMPLETED_QUEUE = "completed_tasks.json"
FAILED_QUEUE = "failed_tasks.json"


class TaskStatus:
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class Task:
    """Represents a task in the queue."""

    def __init__(
        self, task_id: str, target_subagent: str, task_data: dict, priority: int = 0
    ):
        self.task_id = task_id
        self.target_subagent = target_subagent
        self.task_data = task_data
        self.priority = priority
        self.status = TaskStatus.PENDING
        self.created_at = __import__("datetime").datetime.now()
        self.completed_at = None
        self.result = None
        self.error = None

    def to_dict(self) -> dict:
        return {
            "task_id": self.task_id,
            "target_subagent": self.target_subagent,
            "task_data": self.task_data,
            "priority": self.priority,
            "status": self.status,
            "created_at": self.created_at.isoformat(),
            "completed_at": (
                self.completed_at.isoformat() if self.completed_at else None
            ),
            "result": self.result,
            "error": self.error,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Task":
        task = cls(
            task_id=data["task_id"],
            target_subagent=data["target_subagent"],
            task_data=data["task_data"],
            priority=data.get("priority", 0),
        )
        task.status = data.get("status", TaskStatus.PENDING)
        task.completed_at = data.get("completed_at")
        task.result = data.get("result")
        task.error = data.get("error")
        return task


class TaskQueue:
    """Manages a persistent task queue using JSON files."""

    def __init__(
        self,
        queue_file: str = QUEUE_FILE,
        completed_file: str = COMPLETED_QUEUE,
        failed_file: str = FAILED_QUEUE,
    ):
        self.queue_file = Path(queue_file)
        self.completed_file = Path(completed_file)
        self.failed_file = Path("failed_tasks.json")
        self._ensure_files()
        # For test compatibility
        self.queue = []

    def _ensure_files(self):
        """Ensure task queue files exist."""
        for f in [self.queue_file, self.completed_file, self.failed_file]:
            if not f.exists():
                Path(f).touch()

    def _load_queue(self) -> list:
        """Load the queue from file."""
        try:
            with open(self.queue_file, encoding="utf-8") as f:
                content = f.read().strip()
            if not content:
                return []
            lines = [line for line in content.splitlines() if line.strip()]
            return [json.loads(line) for line in lines]
        except Exception:
            return []

    def _save_queue(self, tasks: list):
        """Save the queue to file."""
        with open(self.queue_file, "w", encoding="utf-8") as f:
            f.writelines(json.dumps(task) + "\n" for task in tasks)

    def add_task(
        self, task_id: str, target_subagent: str, task_data: dict, priority: int = 0
    ) -> bool:
        """Add a task to the queue."""
        try:
            task = Task(task_id, target_subagent, task_data, priority)
            with open(self.queue_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(task.to_dict()) + "\n")
            # Update in-memory queue for test compatibility
            self.queue = self._load_queue()
            return True
        except Exception as e:
            print(f"Error adding task: {e}")
            return False

    def get_next_task(self) -> dict | None:
        """Get the next task from the queue (highest priority first)."""
        try:
            with open(self.queue_file, encoding="utf-8") as f:
                lines = [line for line in f.read().splitlines() if line.strip()]

            if not lines:
                return None

            # Parse all tasks
            tasks = [json.loads(line) for line in lines]

            # Sort by priority (highest first) and then by creation time
            tasks.sort(key=lambda t: (t["priority"], t.get("created_at", "")))

            # Get the first (highest priority) task
            task = tasks[0]

            # Remove that task from the lines, rewrite the file without it
            removed_id = task["task_id"]
            remaining_lines = [
                line for line in lines if json.loads(line)["task_id"] != removed_id
            ]
            with open(self.queue_file, "w", encoding="utf-8") as f:
                f.writelines(line + "\n" for line in remaining_lines)

            return task
        except Exception as e:
            print(f"Error reading task queue: {e}")
            return None

    def complete_task(self, task_id: str, result: dict, error: str | None = None):
        """Move a task from queue to completed/failed."""
        # Remove from queue (read first, then rewrite)
        tasks = self._load_queue()
        remaining = [task for task in tasks if task.get("task_id") != task_id]
        self._save_queue(remaining)

        # Add to completed or failed queue
        task_data = {
            "task_id": task_id,
            "result": result,
            "error": error,
            "completed_at": __import__("datetime").datetime.now().isoformat(),
        }

        if error:
            with open(self.failed_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(task_data) + "\n")
        else:
            with open(self.completed_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(task_data) + "\n")

    def list_pending(self) -> list[dict]:
        """Get all pending tasks."""
        tasks = []
        with open(self.queue_file, encoding="utf-8") as f:
            for line in f.read().splitlines():
                if line.strip():
                    task = json.loads(line)
                    if task["status"] == "pending":
                        tasks.append(task)
        return tasks


class TaskManager:
    """High-level interface for task management."""

    def __init__(self, queue_file: str = QUEUE_FILE):
        self.queue = TaskQueue(QUEUE_FILE if queue_file is None else queue_file)

    def submit_task(
        self, target_subagent: str, task_data: dict, priority: int = 0
    ) -> str | None:
        """Submit a new task and return the task ID."""
        task_id = (
            f"task_{__import__('datetime').datetime.now().strftime('%Y%m%d_%H%M%S')}"
        )
        success = self.queue.add_task(task_id, target_subagent, task_data, priority)
        return task_id if success else None

    def get_next(self) -> dict | None:
        """Get the next pending task."""
        return self.queue.get_next_task()

    def complete(self, task_id: str, result: dict, error: str | None = None):
        """Mark a task as completed or failed."""
        self.queue.complete_task(task_id, result, error)


# Example usage
if __name__ == "__main__":
    # Example workflow
    manager = TaskManager()

    # Submit a task
    task_id = manager.submit_task(
        target_subagent="claude_code",
        task_data={"type": "analyze", "content": "test prompt"},
        priority=1,
    )

    # Get and process the task
    task = manager.get_next()
    if task:
        print(f"Processing task: {task['task_id']}")
        # In real usage, would call the subagent here
        manager.complete(
            task.task_id, {"status": "completed", "result": "analysis complete"}
        )
