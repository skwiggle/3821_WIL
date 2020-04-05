import socket
from threading import Thread
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

    def _connection_handler(func) -> ():
        def _wrapper(self, port: int, msg: str = None, sock: socket.socket = None):
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            try:
                sock.connect((self._host, port))
                print(self._local_msg['connected'])
                func(self, port, msg if msg else '', sock)
            except socket.timeout as error:
                print(self._local_msg['attempt_failed'],
                      end=f'\n\t\t -> {error}\n' if self._verbose else '\n',
                      flush=True)
            sock.close()
        return _wrapper

    @_connection_handler
    def log_handler(self, port: int, msg: str = None, sock: socket.socket = None):
        while True:
            try:
                msg = sock.recv(self._buffer).decode('utf-8')
                print(msg)
                if not msg:
                    break
            except:
                continue

    @_connection_handler
    def send_msg(self, port: int, msg: str = None, sock: socket.socket = None):
        try:
            sock.send(msg.encode('utf-8'))
        except AttributeError as error:
            print(self._local_msg['msg_failed'],
                  end=f'\n\t\t -> {error}\n' if self._verbose else '\n',
                  flush=True)


if __name__ == '__main__':
    c = Client()
    t1 = Thread(target=c.log_handler, args=(5555,))
    t2 = Thread(target=c.send_msg(5554, msg='hello'))
    t1.start()
    t2.start()






