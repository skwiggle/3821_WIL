from sys import platform, stderr
import os
import socket
from datetime import datetime as dt
from threading import Thread
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


class Terminal(FileSystemEventHandler):
    """
    A server handler in charge or listening and sending information over sockets.
    the class consists of one/two way connection handling as well as allowing for custom actions upon event change.
    """
    _host: str = 'localhost'
    _buffer: int = 2048
    _stream_active: bool = False
    _timestamp = lambda: dt.now().strftime("%I:%M%p")
    _timeout: float = 3600
    _verbose: bool = False
    local_msg: dict = {
        'server_open': f'{_timestamp()}: established server',
        'server_connect_failed': f'{_timestamp()}: failed to connect to the client',
        'server_closed': f'{_timestamp()}: server closed',
        'connection_closed': f'{_timestamp()}: failed to send message because no connection was found',
        'timeout': f'{_timestamp()}: connection timed out',
        'stream_active': f'{_timestamp()}: please wait until previous message has sent',
        'path_not_exist': f'{_timestamp()}: the path %s does not exist, please use an absolute path with file extension'
    }

    @staticmethod
    def log_path(observer: bool = False) -> str:
        """
        Returns the current log file location or the log's parent directory for the
        watchdog observer to monitor for changes.

        :param observer: should the function return the parent directory
                         location instead? (True = yes)
        """
        if 'win' in platform:
            return f"C:/Users/{os.getlogin()}/AppData/Local/Unity/Editor/{'' if observer else 'Editor.log'}"
        elif 'mac' in platform:
            return f"~/Library/Logs/Unity/{'' if observer else 'Editor.log'}"
        elif ('lin' or 'unix') in platform:
            return f"~/.config/unity3d/{'' if observer else 'Editor.log'}"
        return 'none'

    _path = property(log_path)

    @_path.setter
    def set_log_path(self, path: str):
        if os.path.exists(path):
            self.log_path = path
        else:
            print(self.local_msg['path_not_exist'] % f"'{path}'", flush=True)

    def __init__(self):
        observer = Observer()
        observer.schedule(self, self.log_path(observer=True), False)
        observer.start()
        self.two_way_handler(5554)
        observer.stop()

    def on_modified(self, event):
        with open(self.log_path, 'r') as file:
            self.one_way_handler(5555, package=[line for line in file])

    def _connectionBootstrap(func) -> ():
        """
        Wrapper in charge of initialising and stopping a socket correctly
        as well as stopping the server when an event or error occurs such
        as a timeout event.

        :param func: handler function that should extend the wrapper
        """
        def _wrapper(self, port: int, sock: socket.socket = None):
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(self._timeout)
                s.bind((self._host, port))
                s.listen()
                print(self.local_msg['server_open'])
                try:
                    func(self, port, s)
                except socket.timeout as error:
                    print(self.local_msg['timeout'],
                          end=f'\n\t\t -> {error}\n' if self._verbose else '\n',
                          flush=True)
            exit(0)
        return _wrapper

    @_connectionBootstrap
    def two_way_handler(self, port: int, sock: socket.socket = None):
        """
        Constantly listen for incoming messages from other hosts.

        Should be used to handle incoming log updates from the terminal
        or incoming commands from the application. Also displays error info.

        :param port: port number
        :param sock: parent socket
        """
        commands = {'?', 'get log', 'clear log'}
        while True:
            try:
                client, address = sock.accept()
                with client:
                    while True:
                        reply = client.recv(self._buffer).decode('utf-8')
                        if reply:
                            if reply.lower().replace(' ', '') == 'getlog':
                                with open(self.log_path(), 'r') as file:
                                    self.one_way_handler(5555, package=[line for line in file])
                            print(reply)
                            continue
                        break
            except (socket.timeout, WindowsError) as error:
                print(self.local_msg['timeout'],
                      f'\n\t\t -> {error}\n' if self._verbose else '\n',
                      flush=True)
                break
        print(self.local_msg['server_closed'])

    def one_way_handler(self, port: int, msg: str = None, package: [str] = None):
        """
        Sends a message or an array of messages to server host.

        Should be used to send commands to the terminal or send the current
        Unity debug log information to the application. Also displays error info.

        :param port: port number
        :param msg: the message (defaults to none)
        :param package: a list of messages (defaults to none)
        """
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.connect((self._host, port))
                self._stream_active = True
                if msg:
                    sock.send(msg.encode('utf-8'))
                if package:
                    for line in package:
                        sock.send(line.encode('utf-8'))
                    sock.send('--EOF'.encode('utf-8'))
        except WindowsError as error:
            print(self.local_msg['connection_closed'],
                  f'\n\t\t -> {error}' if self._verbose else '\n',
                  flush=True)
        self._stream_active = False


if __name__ == '__main__':
    t = Terminal()
