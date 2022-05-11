from dataclasses import dataclass, field
from typing import Callable
from uuid import uuid4
from threading import Thread


@dataclass
class Task:
    name: str
    target: Callable
    arguments: dict
    timeout: int = 0
    pre_exec: Callable = field(default=None, repr=False)
    callback: Callable = field(default=None, repr=False)
    return_data: type = field(init=False, default=None, repr=False)
    error: Exception = field(init=False, default=None)
    id: str = field(init=False)

    def __post_init__(self):
        self.__thread = None
        self.__did_run = False
        if type(self.arguments) != dict:
            raise ValueError("arguments property must be a dictionary with "
                             "keys corresponding to target's arguments")
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
            return_data = self.target(**self.arguments)
            self.return_data = return_data
        except Exception as error:
            self.error = error
        self.__did_run = True
        if self.callback:
            self.callback(self)
