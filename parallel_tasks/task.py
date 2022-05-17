import sys
import io
import warnings
import enum
from typing import Callable, Union
from uuid import uuid4
from .pthread import PThread, ThreadKilledException
from .function import Function
from .proxyio import ProxyIO


class InvalidTaskState(Exception):
    pass


class TaskPriority(enum.IntFlag):
    PRIORITY_HIGH = 100
    PRIORITY_MEDIUM = 50
    PRIORITY_LOW = 1
    PRIORITY_UNSPECIFIED = -1


class Task:

    def __init__(self, target: Function, name: str, timeout: int = 0,
                 pre_exec: Function = None, callback: Union[Callable, Function] = None,
                 dependency: 'Task' = None, priority: TaskPriority = TaskPriority.PRIORITY_UNSPECIFIED):
        self.priority = priority
        self.timeout = timeout if timeout > -2 else -1
        self.__thread = None
        self.__target = target
        self.__name = name
        self.__pre_exec = pre_exec
        self.__callback = callback
        self.__return_data = None
        self.__error = None
        self.__id = str(uuid4())
        self.__did_run = False
        self.__running = False
        self.__dependency = dependency
        self.__did_run_at_least_once = False
        self.__did_reset = False
        self.__is_being_killed = False
        self.__stdout = None
        self.__stderr = None
        self.combined_output = True
        # make sure the dependency is an instance of this class
        if self.__dependency and (type(self.__dependency) != type(self)):
            raise Exception(f"Dependecy must be a {self.__class__.__name__} instance")

    @property
    def id(self):
        return self.__id

    @property
    def return_data(self):
        return self.__return_data

    @property
    def error(self):
        return self.__error

    @property
    def name(self):
        return self.__name

    @property
    def is_running(self):
        return self.__running

    @property
    def did_complete(self):
        return self.__did_run

    @property
    def is_being_killed(self):
        return self.__is_being_killed

    @property
    def is_rerun(self):
        if self.__did_run_at_least_once:
            if self.__did_reset:
                return True
        return False

    @property
    def stdout(self):
        if isinstance(sys.stdout, io.StringIO):
            if self.__thread:
                return sys.stdout.getvalue(self.__thread.ident)

    @property
    def stderr(self):
        if isinstance(sys.stderr, io.StringIO):
            if self.__thread:
                return sys.stderr.getvalue(self.__thread.ident)

    def __repr__(self):
        repr = f"{self.__class__.__name__} '{self.name}'"
        status = "Ready to " + ("re-run" if self.is_rerun else "run")
        if self.did_complete:
            status = "Completed "
            if self.is_rerun:
                status += "re-run "
            if self.error:
                status += "with error"
            else:
                status += "sccessfully"
        elif self.is_running:
            status = "Re-running" if self.is_rerun else "Running"
        repr += f" (id: {self.id}, status: {status}"
        if self.__return_data:
            repr += f", output: <{type(self.__return_data).__name__} at {hex(id(self.__return_data))}>"
        repr += ')'
        return repr

    def run(self):
        self.__run_once_guard()
        self.__thread = PThread(target=self.__run_proxy, daemon=False, name=self.name)
        self.__thread.start()

    def run_sync(self):
        self.__run_once_guard()
        self.__run_proxy()

    def reset(self):
        if self.is_running:
            raise InvalidTaskState("Cannot reset tasks that are currently running")
        if not self.did_complete:
            warnings.warn("Resetting task that hasn't run has no effect", Warning)
            return
        self.__unset_output_buffers()
        self.__thread = None
        self.__error = None
        self.__return_data = None
        self.__did_run = False
        self.__did_reset = True

    def stop(self):
        if self.__thread:
            self.__is_being_killed = True
            self.__thread.kill()

    def __run_once_guard(self):
        if self.is_running:
            raise InvalidTaskState("The task is already running")
        if self.did_complete:
            raise InvalidTaskState("The task has already ran to completion")

    def __run_proxy(self):
        if not self.__running:
            self.__running = True
        else:
            return
        if self.__dependency:
            try:
                self.__dependency.run_sync()
            # catch and rethrow stating where it failed
            except Exception as e:
                raise Exception(f"Error while trying to run dependency: {e}")
        self.__set_output_buffers()
        try:
            return_data = self.__target.target(**self.__target.arguments)
            self.__return_data = return_data
        except ThreadKilledException as error:
            self.__killed = True
            self.__error = error
        except Exception as error:
            self.__error = error
        self.__did_run = True
        self.__did_run_at_least_once = True
        self.__running = False
        self.__is_being_killed = False
        if self.__callback:
            self.__post_exec()

    def __set_output_buffers(self):
        # IMPORTANT call this after thread has started
        # becasuse ident is only set after thread is realized

        # create buffers for capturing stdout and stderr
        if not self.__thread or not (thread_id := self.__thread.ident):
            return
        stdout = io.StringIO()
        stderr = stdout if self.combined_output else io.StringIO()
        if isinstance(sys.stdout, ProxyIO):
            sys.stdout.register_buf_for_id(stdout, thread_id)
        if isinstance(sys.stderr, ProxyIO):
            sys.stderr.register_buf_for_id(stderr, thread_id)

    def __unset_output_buffers(self):
        if not self.__thread or not (thread_id := self.__thread.native_id):
            return
        if isinstance(sys.stdout, ProxyIO):
            sys.stdout.deregister_buf_for_id(thread_id)
        if isinstance(sys.stderr, ProxyIO):
            sys.stderr.deregister_buf_for_id(thread_id)

    def __post_exec(self):
        if callable(self.__callback):
            self.__callback(self)
        elif type(self.__callback) is Function:
            self.__callback.target(self)

    def __del__(self):
        # some cleanup
        self.__unset_output_buffers()
