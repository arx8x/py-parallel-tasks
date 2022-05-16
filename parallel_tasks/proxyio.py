import io
import threading


class ProxyIO(io.StringIO):

    def __init__(self, original_buf: io.TextIOWrapper, initial_value='', newline='\n'):
        if not isinstance(original_buf, io.TextIOWrapper):
            raise ValueError("original_buf must be a StringIO")
        self.__orig_buf = original_buf
        self.__proxies = {threading.main_thread().ident: original_buf}
        super().__init__(initial_value=initial_value, newline=newline)

    def __select_buf(self) -> io.StringIO:
        thread_id = threading.current_thread().ident
        if thread_id not in self.__proxies:
            self.__proxies[thread_id] = io.StringIO()
        return self.__proxies.get(thread_id, self.__orig_buf)

    def read(self, size):
        self.__select_buf().read(size)

    def write(self, s):
        self.__select_buf().write(s)

    def getvalue(self, thread_id: int = None):
        if not thread_id:
            thread_id = threading.current_thread().ident
        if isinstance(self.__proxies.get(thread_id), io.StringIO):
            return self.__proxies.get(thread_id).getvalue()

    @property
    def original_buf(self):
        return self.__orig_buf
