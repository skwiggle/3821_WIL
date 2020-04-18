# -*- coding: utf-8 -*-
import re
import time
from sys import platform, stderr
import os
import socket
from datetime import datetime as dt
from threading import Thread
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


class Timer(Thread):
    """
    Custom timer that starts and counts down from an (interval) once
    a unity log file has been updated, the counter resets if updated again.

    The class itself does not handle observer and socket objects, it is used
    as only a timer extending a thread object meaning it can only be ran once.
    However, resetting the timer does not complete the thread just as the timer
    reset cannot be ran after the thread has finished.
    """
    def __init__(self, interval):
        Thread.__init__(self)
        self.max_num, self.current_num = interval, interval
        self.active = False

    def reset(self):
        """ Reset the timer """
        self.current_num = self.max_num

    def run(self) -> None:
        """ continue to countdown to 0 """
        self.active = True
        while self.current_num != 0:
            print(self.current_num)
            time.sleep(1)
            self.current_num -= 1
        self.active = False


class Terminal(FileSystemEventHandler):
    """
    A server handler in charge or listening and sending information over sockets.
    the class consists of one/two way connection handling and checking for filesystem
    changes for log files.
    """
    _host: str = 'localhost'
    _buffer: int = 2048
    _stream_active: bool = False
    _timestamp = lambda msg: f'{dt.now().strftime("%I:%M%p")}: {msg}'
    _timeout: float = 3600
    _verbose: bool = False
    _stream_delay: Timer = Timer(3)
    local_msg: dict = {
        'server_open': _timestamp('established server'),
        'server_connect_failed': _timestamp('failed to connect to the client'),
        'server_closed': _timestamp('server closed'),
        'connection_closed': _timestamp('failed to send message because no connection was found'),
        'timeout': _timestamp('connection timed out'),
        'stream_active': _timestamp("log file was updated while being sent, either wait for another update or "
                                    "retrieve manually using \'get log\'"),
        'stream_complete': _timestamp('log file sent to client'),
        'path_not_exist': _timestamp('the path %s does not exist, please use an absolute path with file extension'),
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

    def __init__(self, unittest: bool = False):
        """
        Initialise the server class by creating an observer object to monitor
        for unity debug log file changes and start main server. Observer and program
        stop once server shuts down.
        """
        if not unittest:
            observer = Observer()
            observer.schedule(self, self.log_path(observer=True), False)
            observer.start()
            self.two_way_handler(5554)
            observer.stop()

    def on_modified(self, event):
        if self._stream_delay.active and self._stream_active:
            self._stream_delay.reset()
        if not self._stream_delay.active and self._stream_active:
            self._stream_delay = Timer(3)
            self._stream_delay.start()
            self._stream_delay()
        elif not self._stream_delay.active and not self._stream_active:
            if os.stat(event.src_path).st_size == 0:
                print(self.local_msg['stream_complete'], flush=True)
                self.one_way_handler(5555, f'tg:>')
            else:
                with open(event.src_path, 'r') as file:
                    self.one_way_handler(5555, package=
                        [line for line in file])
                    self.one_way_handler(5555, msg='--EOF')
                with open(event.src_path, 'w'): pass
        elif self._stream_delay.active and not self._stream_active:
            pass

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
        while True:
            try:
                client, address = sock.accept()
                with client:
                    while True:
                        reply = client.recv(self._buffer).decode('utf-8')
                        if reply:
                            if reply[:4] == 'uc:>':
                                print(reply[4:])
                                self.one_way_handler(5555, 'tg:>unity log file empty')
                                break
                            elif reply[:4] == 'kc:>':
                                if reply[4:] == 'get log':
                                    log_path = self.log_path()
                                    if os.stat(log_path).st_size == 0:
                                        print(self.local_msg['stream_complete'], flush=True)
                                        self.one_way_handler(5555, f'tg:>')
                                        break
                                    with open(log_path, 'r') as file:
                                        self.one_way_handler(5555, package=
                                        [line for line in file])
                                        self.one_way_handler(5555, msg='--EOF')
                                    with open(log_path, 'w'): pass
                            continue
                        break
            except (socket.timeout, WindowsError) as error:
                print(self.local_msg['timeout'],
                      f'\n\t\t -> {error}\n' if self._verbose else '\n',
                      flush=True)
                break
        print(self.local_msg['server_closed'])

    def one_way_handler(self, port: int, msg: str = None, package: [str] = None) -> bool:
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
                    self._stream_active = False
                    return True
                if package:
                    for line in package:
                        sock.send(line.encode('utf-8'))
                    sock.send('--EOF'.encode('utf-8'))
                    self._stream_active = False
                    return True
        except WindowsError as error:
            print(self.local_msg['connection_closed'],
                  f'\n\t\t -> {error}' if self._verbose else '\n',
                  flush=True)
        return False


if __name__ == '__main__':
    t = Terminal()
