import socket
from datetime import datetime as dt


class Client:
    _host: str = 'localhost'
    _buffer: int = 2048
    _log_sock: socket.socket = None
    _cmd_sock: socket.socket = None
    _active: bool = False
    _verbose: bool = False
    _timestamp = lambda: dt.now().strftime("%I:%M%p")
    _local_msg: dict = {
        'connected': f'{_timestamp()}: connected to server',
        'attempt_failed': f'{_timestamp()}: failed to connect to server',
        'msg_failed': f'{_timestamp()}: message failed to send because no active connection was found'
    }

    def _connection_handler(func: ()) -> ():
        def _wrapper(self, msg: str, port: int):
            self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._sock.settimeout(2)
            try:
                self._sock.connect((self._host, port))
                print(self._local_msg['connected'])
                func(self, msg, port)
            except socket.timeout as error:
                print(self._local_msg['attempt_failed'],
                      end=f'\n\t\t -> {error}\n' if self._verbose else '\n',
                      flush=True)
            self._sock.close()
        return _wrapper

    @_connection_handler
    def log_handler(self, msg: str, port: int):
        while True:
            try:
                msg = self._log_sock.recv(self._buffer).decode('utf-8')
                print(msg)
            except:
                continue

    @_connection_handler
    def send_msg(self, msg: str, port: int):
        try:
            self._cmd_sock.send(msg.encode('utf-8'))
        except AttributeError as error:
            print(self._local_msg['msg_failed'],
                  end=f'\n\t\t -> {error}\n' if self._verbose else '\n',
                  flush=True)


if __name__ == '__main__':
    c = Client()





