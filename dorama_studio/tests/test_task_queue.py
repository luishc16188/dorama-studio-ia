from dorama_studio.orchestration.task_queue import Task, TaskQueue

# Test basic functionality
task = Task(
    task_id="test_001",
    target_subagent="claude_code",
    task_data={"action": "analyze"},
    priority=1,
)

# Test basic operations
print(f"Task ID: {task.task_id}")
print(f"Task status: {task.status}")

# Test queue operations
queue = TaskQueue()
queue.add_task("task_001", "claude_code", {"test": "data"}, priority=1)
print(f"Queue has tasks: {len(queue.queue) > 0}")

# Test task completion
manager = __import__(
    "dorama_studio.orchestration.task_queue", fromlist=["manager"]
).TaskManager()
manager.complete("task_001", {"status": "completed", "result": "success"}, error=None)

print("Task queue test completed successfully")
