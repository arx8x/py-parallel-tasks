from dataclasses import dataclass, field
from typing import Callable, Union, Iterable, Mapping


@dataclass(frozen=True)
class Function:
    target: Callable
    arguments: Union[Mapping, Iterable] = field(default_factory=list)

    def __post_init__(self):
        if not callable(self.target):
            raise TypeError("target must be a callable")

    def excecute(self):
        if isinstance(self.arguments, Mapping):
            return self.target(**self.arguments)
        elif isinstance(self.arguments, Iterable):
            return self.target(*self.arguments)
        else:
            raise AttributeError("Function arguments must be iterable or mapping")
