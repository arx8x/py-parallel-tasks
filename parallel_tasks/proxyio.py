import io
import threading


class ProxyIO(io.StringIO):

    def __init__(self, original_buf: io.TextIOWrapper, initial_value='', newline='\n'):
        if not isinstance(original_buf, io.TextIOWrapper):
            raise ValueError("original_buf must be a StringIO")
        self.__orig_buf = original_buf
        self.__proxies = {threading.main_thread().native_id: original_buf}
        super().__init__(initial_value=initial_value, newline=newline)

    def __select_buf(self) -> io.StringIO:
        thread_id = threading.current_thread().native_id
        if thread_id not in self.__proxies:
            self.__proxies[thread_id] = io.StringIO()
        return self.__proxies.get(thread_id, self.__orig_buf)

    def register_buf_for_id(self, buf: io.StringIO, id: int):
        if not isinstance(buf, io.StringIO):
            raise ValueError("buf must be a StringIO")
        self.__proxies[id] = buf

    def deregister_buf_for_id(self, id: int):
        try:
            del(self.__proxies[id])
        except KeyError:
            pass

    def read(self, size):
        self.__select_buf().read(size)

    def write(self, s):
        self.__select_buf().write(s)

    def getvalue(self, id: int = None):
        if not id:
            id = threading.current_thread().native_id
        if isinstance(self.__proxies.get(id), io.StringIO):
            buf = self.__proxies.get(id)
            return buf.getvalue()

    @property
    def original_buf(self):
        return self.__orig_buf
