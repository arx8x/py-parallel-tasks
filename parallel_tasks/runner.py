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
        self.polling_rate = 0.5
        self.__failed_tasks = []
        self.__task_pool = []
        self.__stop_flag = False

    @property
    def failed_tasks(self):
        return self.__failed_tasks

    def run_all(self):
        # copy the array so popping or sorting won't mutate the original ivar
        task_queue = self.__tasks.copy()
        # sort tasks based on priority
        task_queue = sorted(task_queue, key=lambda x: x.priority, reverse=True)
        # run as long as there are active threads "and" tasks in the queue
        while self.__task_pool or task_queue:
            # check for finished tasks and carry out post-exec tasks
            new_task_pool = []
            for task in self.__task_pool:
                if task.did_complete:
                    if callable(self.__callback):
                        self.__callback(task)
                    if task.error:
                        self.__failed_tasks.append(task)
                else:
                    new_task_pool.append(task)
                    # TODO: termination procedure
            self.__task_pool = new_task_pool
            if self.__stop_flag:
                if not self.__task_pool:
                    break
                sleep(self.polling_rate)
                continue
            slots_left = self.__max_parallel - len(self.__task_pool)
            for _ in range(slots_left):
                if not task_queue:
                    break
                task = task_queue.pop(0)
                self.__task_pool.append(task)
                task.run()
            sleep(self.polling_rate)

    def stop(self, force=False):
        self.__stop_flag = True
        if force:
            for task in self.__task_pool:
                task.stop()
