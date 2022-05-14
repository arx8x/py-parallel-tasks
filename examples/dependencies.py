from parallel_tasks import Task, Function
import time


def main_task():
    print("running main task")
    time.sleep(1)
    print("completed main task")


def dependency_task():
    print("running dependency_task task")
    raise Exception('random exception')
    time.sleep(1)
    print("completed dependency_task task")


def primordial_task():
    print("primordial_task start")
    time.sleep(1)
    print("primordial_task completed")


task1 = Task(target=Function(primordial_task), name="primordial")
task2 = Task(target=Function(dependency_task), name="dependency", dependency=task1)
task3 = Task(target=Function(main_task), dependency=task2, name="main")

# we want to run task3
# task3 depends on task2. So task2 is run first
# since task2 depends on task1. it's run before that.
# Because of the dependency chain, tasks are run in order
# task1 -> task2 -> task3

# dependency tasks don't get their own thread. They're run in
# whichever thread the dependent runs on.

# If task3 is run synchronously (run_sync()), the execution is in main thread
# So its dependency, task2 and task2's dependency, task3 are also run in main thread
# If task3 is run asynchronously (run()), task3 gets a new thread. The whole of
# the dependency chain will run in that new thread.
# Dependencies don't get new additional threads
task3.run()


time.sleep(5)
for task in [task1, task2, task3]:
    if task.error:
        print(f"The task '{task.name}' had an error: {task.error}")
