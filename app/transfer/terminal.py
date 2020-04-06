import socket
from datetime import datetime as dt
from sys import stdout, platform, stderr
import os
from threading import Thread
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from app.transfer.server import Server


class Terminal(FileSystemEventHandler):
    """
    A server handler in charge or listening and sending information over sockets

    the class consists of one/two way connection handling as well as allowing for
    custom actions upon event change.
    """
    _host: str = 'localhost'
    _buffer: int = 2048
    _temp_log_folder: str = './log/'
    _stream_active: bool = False
    _timestamp = lambda: dt.now().strftime("%I:%M%p")
    _timeout: float = 3600
    _verbose: bool = False
    local_msg: dict = {
        'server_open': f'{_timestamp()}: established server',
        'server_closed': f'{_timestamp()}: server closed',
        'connection_closed': f'{_timestamp()}: failed to send message because no connection was found',
        'timeout': f'{_timestamp()}: connection timed out',
        'stream_active': f'{_timestamp()}: please wait until previous message has sent'
    }

    def __init__(self):
        observer = Observer()
        observer.schedule(self, self._temp_log_folder, False)
        observer.start()
        self.two_way_handler(5554)
        observer.stop()

    def on_modified(self, event):
        with open(self.log_path(), 'r') as file:
            self.one_way_handler(5554, package=[line for line in file])

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
        :param handler_name: name of handler, usually 'log' or 'cmd'
        :param sock: parent socket
        """
        try:
            client, address = sock.accept()
            with client:
                while True:
                    reply = client.recv(self._buffer).decode('utf-8')
                    if reply:
                        print(reply)
                        if reply == 'LOG':
                            with open(self.log_path(), 'r') as file:
                                self.one_way_handler(5554, package=[line for line in file])
        except WindowsError as error:
            print(self.local_msg['server_closed'],
                  f'\n\t\t -> {error}\n' if self._verbose else '\n',
                  flush=True)
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
        except WindowsError as error:
            print(self.local_msg['connection_closed'],
                  f"\n\t\t -> {error}\n' if self._verbose else '\n",
                  flush=True)
        self._stream_active = False

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
        raise FileNotFoundError("log path does not exist")


if __name__ == '__main__':
    t = Terminal()
    t1 = Thread(target=t.two_way_handler, args=(5554,))
    t2 = Thread(target=t.one_way_handler, args=(5554, None, [str(x) for x in range(100)]))
    t1.start()
    t2.start()
    t1.join()
