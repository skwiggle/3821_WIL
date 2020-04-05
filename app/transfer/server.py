import os
from sys import stderr, stdout, platform
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import socket
from threading import Thread
from datetime import datetime as dt
from typing import Iterable


class Server(FileSystemEventHandler):
    _host: str = 'localhost'
    _buffer: int = 2048
    _cmd_client: socket.socket = None
    _cmd_handler_port_active: bool = False
    _log_client: socket.socket = None
    _log_handler: bool = False
    _timestamp = lambda: dt.now().strftime("%I:%M%p")
    _timeout: float = 2
    _verbose: bool = False
    _local_msg: dict = {
        'started': f'{_timestamp()}: server is running',
        'closed': f'{_timestamp()}: server closed',
        'timeout': f'{_timestamp()}: server closed after an hour of inactivity',
        'connection_closed': f'{_timestamp()}: client disconnected',
        'log_closed': f'{_timestamp()}: log sent to client'
    }

    def __init__(self, verbose: bool = False, timeout: float = 60):
        self._verbose = verbose
        self._timeout = timeout

    def _connectionBootstrap(func) -> ():
        def _wrapper(self, port: int, client: socket.socket = None):
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(self._timeout)
                sock.bind((self._host, port))
                sock.listen()
                try:
                    client, address = sock.accept()
                    with client:
                        func(self, port, client)
                except socket.timeout as error:
                    print(self._local_msg['timeout'],
                          end=f'\n\t\t -> {error}\n' if self._verbose else '\n',
                          flush=True)
        return _wrapper

    @_connectionBootstrap
    def cmd_handler(self, port: int, client: socket.socket = None) -> None:
        self._cmd_handler_port_active = True
        while self._cmd_handler_port_active:
            try:
                msg = client.recv(self._buffer).decode('utf-8')
                print(msg)
                if msg == 'LOG':
                    values = (line for line in open(self.log_path(), 'r'))
                    while True:
                        try:
                            client.send(next(values).encode('utf-8'))
                        except:
                            print(self._local_msg['log_closed'], end='\n', flush=True)
                            break
            except WindowsError as error:
                print(self._local_msg['connection_closed'],
                      end=f'\n\t\t -> {error}\n' if self._verbose else '\n',
                      flush=True)
                break
        print(self._local_msg['closed'])
        exit(0)

    @_connectionBootstrap
    def send_log(self, port: int, client: socket.socket = None):
        self._log_handler = True

    @staticmethod
    def log_path() -> str:
        if 'win' in platform:
            return f'C:/Users/{os.getlogin()}/AppData/Local/Unity/Editor/Editor.log'
        elif 'mac' in platform:
            return '~/Library/Logs/Unity/Editor.log'
        elif ('lin' or 'unix') in platform:
            return '~/.config/unity3d/Editor.log'
        return 'none'


if __name__ == '__main__':
    s = Server(verbose=True)
