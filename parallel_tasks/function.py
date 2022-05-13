from dataclasses import dataclass, field
from typing import Callable


@dataclass
class Function:
    target: Callable
    arguments: dict = field(default_factory=dict)

    def __post_init__(self):
        if not callable(self.target):
            raise TypeError("target must be a callable")
