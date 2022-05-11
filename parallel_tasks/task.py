from dataclasses import dataclass, field
from typing import Callable
from uuid import uuid4


@dataclass
class Task:
    name: str
    target: Callable
    arguments: dict
    timeout: int = 0
    post_exec: Callable = None
    pre_exec: Callable = None
    return_data: type = field(init=False, default=None)
    error: Exception = field(init=False, default=None)
    id: str = field(init=False)

    def __post_init__(self):
        if type(self.arguments) != dict:
            raise ValueError("arguments property must be a dictionary with "
                             "keys corresponding to target's arguments")
        if self.timeout < -1:
            self.timeout = -1

        if not self.__dict__.get('id'):
            self.__dict__['id'] = str(uuid4())
