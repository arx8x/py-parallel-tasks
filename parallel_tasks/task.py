from dataclasses import dataclass, field
from typing import Callable, Union
from uuid import uuid4
from threading import Thread
from .function import Function


@dataclass
class Task:
    name: str
    target: Function
    timeout: int = 0
    pre_exec: Function = field(default=None, repr=False)
    callback: Union[Callable, Function] = field(default=None, repr=False)
    return_data: type = field(init=False, default=None, repr=False)
    error: Exception = field(init=False, default=None)
    id: str = field(init=False)

    # def __init__(self, target: Function, arguments: dict, name: str,
    #              timeout: int = 0, pre_exec, ):
    #

    def __post_init__(self):
        self.__thread = None
        self.__did_run = False

        if self.timeout < -1:
            self.timeout = -1

        if not self.__dict__.get('id'):
            self.__dict__['id'] = str(uuid4())

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
            return_data = self.target.target(**self.target.arguments)
            self.return_data = return_data
        except Exception as error:
            self.error = error
        self.__did_run = True
        if self.callback:
            self.__post_exec()

    def __post_exec(self):
        if callable(self.callback):
            self.callback(self)
        elif type(self.callback) is Function:
            self.callback.target(self)
