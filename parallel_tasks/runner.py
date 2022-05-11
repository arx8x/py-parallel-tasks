from typing import Callable
from time import sleep


class ParallelRunner:

    def __init__(self, tasks: list, callback: Callable = None, max_parallel: int = 4):
        for task in tasks:
            if task.is_running or task.did_complete:
                raise Exception(f"Cannot add task {task.name} ({task.id}) to task queue because "
                                f"it's either running or completed running")
        self.__tasks = tasks
        self.__callback = callback
        self.__max_parallel = max_parallel

    def run_all(self):
        # copy the array so popping won't mutate the original argument
        task_queue = self.__tasks.copy()
        task_pool = []
        # run as long as there are active threads "and" tasks in the queue
        while task_pool or task_queue:
            # check for finished tasks and carry out post-exec tasks
            for task in task_pool:
                if task.did_complete:
                    task_pool.remove(task)
                    # TODO: termination procedure

            slots_left = self.__max_parallel - len(task_pool)
            for _ in range(slots_left):
                if not task_queue:
                    break
                task = task_queue.pop()
                task_pool.append(task)
                task.run()
            sleep(0.5)
