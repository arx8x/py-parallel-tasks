from typing import Callable, Union
from uuid import uuid4
from threading import Thread
from .function import Function


class Task:

    def __init__(self, target: Function, name: str, timeout: int = 0,
                 pre_exec: Function = None, callback: Union[Callable, Function] = None):
        self.__thread = None
        self.__target = target
        self.__name = name
        self.timeout = timeout if timeout > -2 else -1
        self.__pre_exec = pre_exec
        self.__callback = callback
        self.__return_data = None
        self.__error = None
        self.__id = str(uuid4())
        self.__did_run = False

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
        if self.__thread:
            if self.__thread.is_alive():
                return True
        return False

    @property
    def did_complete(self):
        return self.__did_run

    @property
    def thread_exit(self):
        return not self.__thread.is_alive()

    def __repr__(self):
        repr = f"{self.__class__.__name__} {self.name}"
        status = "Ready to run"
        if self.did_complete:
            status = "Completed "
            if self.error:
                status += "with error"
            else:
                status += "sccessfully"
        elif self.is_running:
            status = "Running"
        repr += f" (id: {self.id}, status: {status}"
        if self.__return_data:
            repr += f", output: <{type(self.__return_data).__name__} at {hex(id(self.__return_data))}>"
        repr += ')'
        return repr

    def run(self):
        if self.is_running:
            raise Exception("The task is already running")
        if self.did_complete:
            raise Exception("The task has ran to completion")
        self.__thread = Thread(target=self.__run_proxy, daemon=False, name=self.name)
        self.__thread.start()

    def __run_proxy(self):
        if not self.is_running:
            return
        try:
            return_data = self.__target.target(**self.__target.arguments)
            self.__return_data = return_data
        except Exception as error:
            self.__error = error
        self.__did_run = True
        if self.__callback:
            self.__post_exec()

    def __post_exec(self):
        if callable(self.__callback):
            self.__callback(self)
        elif type(self.__callback) is Function:
            self.__callback.target(self)
