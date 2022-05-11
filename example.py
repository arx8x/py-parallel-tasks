from parallel_tasks import Task, ParallelRunner, Function
import random
import time
import hashlib
from threading import current_thread
# create some long running tasks


def wait_function(s=6):
    # this function just efficiently and pateiently waits
    # to return nothing
    thread_name = current_thread().name
    print(f"wait_function has begun on '{thread_name}' thread")
    time.sleep(s)
    print(f"wait_function has finished on '{thread_name}' thread")


def iter_function(iters: int, print_stats: bool):
    # runs sha1 hashing on random bytes n number of times
    thread_name = current_thread().name
    print(f"iter_function has started on '{thread_name}' thread for {iters} iterations")
    c = 0
    t1 = time.time()
    for _ in range(iters):
        bytes = random.randbytes(0xfffff)
        hashlib.sha1(bytes).hexdigest()
        c += 1
    tdelta = time.time() - t1
    if print_stats:
        print(f"hashing {c} took {tdelta} seconds")
    print(f"iter_function has finished on '{thread_name}'")
    return tdelta


def thanos_function():
    # this function has a 50% chance of failing
    time.sleep(2)
    outcome = random.randint(0, 1)
    if outcome:
        raise Exception("I am Ironman")
    return "I am Thanos"


def task_finished_callback(task: Task):
    # this is the callback we'll use when creating Task objects
    print(f"[CALLBACK] The task {task.name} ({task.id}) has completed")
    if task.error:
        print(f"The task failed '{task.error}'")


# create first task
# second argument to Function is the list of arguments as kwargs dict
task1_function = Function(iter_function, {'iters': 1000, 'print_stats': True})
task1 = Task(name="iter1000", target=task1_function)

# for task2, we're assigning a callback too, so we'll know when the task has finished
task2 = Task(name='wait1', target=Function(wait_function, {}), callback=task_finished_callback)

# choosing not to print stats for task 3
task3_function = Function(iter_function, {'iters': 2000, 'print_stats': False})
task3 = Task(name="iter2000", target=task3_function)

# task4's function will return data but it has a chance of failing
# we're assigining it a callback and see if it failed
task4 = Task(name='snap1', target=Function(thanos_function, {}), callback=task_finished_callback)


# create a runner instance that will run 2 tasks at once
runner = ParallelRunner(tasks=[task1, task2, task3, task4])
# start all tasks. The function will exit once all tasks are completed
# code after the following call will be executed only after all tasks
# are completed
# if you wish to do something when a specific Task finishes,
# assign a 'callback' to that particular Task
runner.run_all()


# print task3's output to see how long it took for 1000 iterations
print(f"output of task3 -> {task3.return_data} seconds for 2000 iterations")

if not task4.error:
    # print task4's output since it returns data too
    print(f"output of task4 -> {task4.return_data}")
