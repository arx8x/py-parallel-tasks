from .runner import ParallelRunner
from .task import Task, InvalidTaskState, TaskPriority
from .function import Function
from .pthread import ThreadKilledException
from .proxyio import ProxyIO
import sys

globals().update(TaskPriority.__members__)

__all__ = ['ParallelRunner', 'Task', 'Function', 'InvalidTaskState', 'ThreadKilledException',
           'enable_threaded_output',
           'PRIORITY_LOW', 'PRIORITY_HIGH', 'PRIORITY_MEDIUM', 'PRIORITY_UNSPECIFIED']


def enable_threaded_output():
    # steal stderr and stdout from sys
    stdout = ProxyIO(original_buf=sys.stdout)
    if not isinstance(sys.stdout, ProxyIO):
        sys.stdout = stdout
    if not isinstance(sys.stderr, ProxyIO):
        sys.stderr = stdout
