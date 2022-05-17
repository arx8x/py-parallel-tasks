from .runner import ParallelRunner
from .task import Task, InvalidTaskState, TaskPriority
from .function import Function
from .pthread import ThreadKilledException
from .proxyio import ProxyIO
import sys

globals().update(TaskPriority.__members__)

__all__ = ['ParallelRunner', 'Task', 'Function', 'InvalidTaskState', 'ThreadKilledException',
           'enable_threaded_output', 'disable_threaded_output',
           'PRIORITY_LOW', 'PRIORITY_HIGH', 'PRIORITY_MEDIUM', 'PRIORITY_UNSPECIFIED']


def enable_threaded_output():
    # steal stderr and stdout from sys
    if not isinstance(sys.stdout, ProxyIO):
        stdout = ProxyIO(original_buf=sys.stdout)
        sys.stdout = stdout

    if not isinstance(sys.stderr, ProxyIO):
        stderr = ProxyIO(original_buf=sys.stderr)
        sys.stderr = stderr


def disable_threaded_output():
    # restore stored original stdout and stderr
    if isinstance(sys.stdout, ProxyIO):
        sys.stdout = sys.stdout.original_buf
    if isinstance(sys.stderr, ProxyIO):
        sys.stderr = sys.stderr.original_buf
