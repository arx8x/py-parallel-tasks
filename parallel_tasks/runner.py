from threading import Thread, Semaphore, current_thread
from typing import Callable
from time import sleep
from .task import Task


class ParallelRunner:

    def __init__(self, tasks: list, callback: Callable = None, max_parallel: int = 4):
        self.__tasks = tasks
        self.__callback = callback
        self.__max_parallel = max_parallel

    def run_all(self):
        # this wrapper makes it possible to capture output from the 'target'
        def _wrapper(task: Task):
            try:
                return_data = task.target(**task.arguments)
                task.return_data = return_data
            except Exception as error:
                task.error = error
        # copy the array so popping won't mutate the original argument
        task_queue = self.__tasks.copy()
        thread_pool = []
        # run as long as there are active threads "and" tasks in the queue
        while thread_pool or task_queue:
            # check for finished tasks and carry out post-exec tasks
            for thread in thread_pool:
                if not thread.is_alive():
                    thread_pool.remove(thread)
                    # TODO: termination procedure

            slots_left = self.__max_parallel - len(thread_pool)
            for _ in range(slots_left):
                if not task_queue:
                    break
                task = task_queue.pop()
                # call the wrapper with the task as argument
                thread = Thread(target=_wrapper, name=task.id, args=[task], daemon=False)
                thread.start()
                thread_pool.append(thread)
            sleep(0.5)
