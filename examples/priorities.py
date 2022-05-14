import parallel_tasks
import random
import time

# Simple concept
# Tasks with higher priority run first
# Unspecified priority can run whenever, even before high priority tasks


def target_function():
    time.sleep(2)


def callback(task):
    # callback to know when the task has finished
    print(f"{task.name} has finished (priority: {str(task.priority)})")


priorities = list(parallel_tasks.TaskPriority.__members__.values())
print(priorities)
# generate 10 tasks with random priorities
tasks = []
for i in range(10):
    task = parallel_tasks.Task(
                target=parallel_tasks.Function(target_function),
                name=f"task_{i}",
                callback=callback,
                priority=random.choice(priorities))
    tasks.append(task)

# 2 tasks will run at the same time
runner = parallel_tasks.ParallelRunner(tasks, max_parallel=2)
runner.run_all()
# the callback will be executed each time a task finishes
# it can be observed that tasks with higher priority get
# executed first
