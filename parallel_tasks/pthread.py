from threading import Thread
import sys


class ThreadKilledException(Exception):
    pass


class PThread(Thread):
    def run(self):
        self.__exit = False
        sys.settrace(self.__trace)
        super().run()

    def __trace(self, frame, event, args):
        # exits and exceptions in 'call' seem to be ignored.
        # So, we need a line execution after __exit is set to
        # kill the thread
        # This wouldn't work in situations where the thread is waiting
        # for something. For example, waiting for an event, lock, semaphore
        # or sleep(). A line must be exectued for this to work
        # If exiting in 'call' event worked, all there's needed is
        # check if frame.f_code.co_name is 'kill' (the method name) and exit
        if event == 'line':
            if self.__exit:
                raise ThreadKilledException()
        return self.__trace

    def kill(self):
        self.__exit = True
