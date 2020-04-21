# -*- coding: utf-8 -*-
import os
import shutil
from sys import platform
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from threading import Thread
from datetime import datetime as dt
import socket
import time
import re

_timestamp = lambda msg: f'{dt.now().strftime("%c")}: {msg}'
# noinspection PyArgumentList
log_file_names: set = {'Editor.log', 'Editor_prev.log', 'upm.log'}
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
    'watchdog_update': _timestamp('automatic unity log update, sending updated log files...')
}


def log_path(log_name: str = 'Editor.log', observer: bool = False) -> str:
    """
    Returns the current log file location or the log's parent directory for the
    watchdog observer to monitor for changes.

    :param log_name: name of log file, can be one of the following
                        - Editor.log
                        - Editor-prev.log
                        - upm.log
    :param observer: should the function return the parent directory
                     location instead? (True = yes)
    """
    if 'win' in platform:
        return f"C:/Users/{os.getlogin()}/AppData/Local/Unity/Editor/{'' if observer else log_name}"
    elif 'mac' in platform:
        return f"~/Library/Logs/Unity/{'' if observer else log_name}"
    elif ('lin' or 'unix') in platform:
        return f"~/.config/unity3d/{'' if observer else log_name}"
    return 'no path found'


class IsolatedSender:
    """
    Extension of the Terminal class but can only send log files built to be
    handled by the timer class. Should only be triggered after the timer has
    completed.
    """
    _host = 'localhost'
    _verbose: bool = False

    def __init__(self, temp_log_name: str, verbose: bool = False):
        self._verbose = verbose
        self.temp_log_name = temp_log_name

    def one_way_handler(self, port: int, msg: str = None, package: [str] = None) -> bool:
        """
        Sends a message or an array of messages to application.

        Should be used to receive commands from the app or send the current
        Unity debug log information to the application. Also displays error info.

        :param port: port number
        :param msg: the message (defaults to none)
        :param package: a list of messages (defaults to none)
        """
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.connect((self._host, port))
                # send the message if message not blank
                if msg:
                    sock.send(msg.replace('\t', '').encode('utf-8'))
                    return True
                # send a list of messages if package not blank
                if package:
                    for line in package:
                        sock.send(line.replace('\t', '').encode('utf-8'))
                    sock.send('--EOF'.encode('utf-8'))
                    return True
        except WindowsError as error:
            with open('terminal_log.txt', 'a+') as file:
                print(local_msg['connection_closed'],
                      f'\n\t\t -> {error}' if self._verbose else '',
                      file=file, flush=True)
        return False

    def clear_temp_log(self) -> bool:
        try:
            temp = f'{log_path(observer=True)}{self.temp_log_name}'
            with open(temp, 'r') as file:
                contents = [line for line in file]
                contents.append('--EOF')
                self.one_way_handler(5555, package=contents)
            with open(re.sub('temp-', '', log_path(self.temp_log_name)), 'w'):
                pass
            os.remove(temp)
            return True
        except Exception as error:
            with open('terminal_log.txt', 'a+') as file:
                print(local_msg['timeout'],
                      end=f'\n\t\t -> {error}' if self._verbose else '\n',
                      file=file, flush=True)
            return False


class Timer(Thread, IsolatedSender):
    """
    Custom timer that starts and counts down from an (interval) once
    a unity log file has been updated, the counter resets if updated again.

    The class itself does not handle observer and socket objects, it is used
    as only a timer extending a thread object meaning it can only be ran once.
    However, resetting the timer does not complete the thread just as the timer
    reset cannot be ran after the thread has finished.
    """
    active: bool = False

    def __init__(self, interval: float, temp_log_name: str, verbose: bool = False):
        Thread.__init__(self)
        IsolatedSender.__init__(self, temp_log_name, verbose)
        self.current_num = interval
        self.max_num = interval
        self.active = False

    def reset(self):
        """ Reset the timer """
        self.current_num = self.max_num

    def run(self) -> None:
        """ continue to countdown to 0 """
        self.active = True
        while self.current_num != 0:
            print(f'will send in: {self.current_num} seconds')
            time.sleep(1)
            self.current_num -= 1
        self.clear_temp_log()
        self.active = False
        print(f"{dt.now().strftime('%c')}: ready to send log", flush=True)


# noinspection PyUnusedLocal
class Terminal(FileSystemEventHandler):
    """
    A server handler in charge or listening and sending information over sockets.
    the class consists of one/two way connection handling and checking for filesystem
    changes for log files.
    """
    _host: str = 'localhost'
    _buffer: int = 2048
    _timeout: float = 3600
    _verbose: bool = False
    _stream_delay: Timer = None

    def __init__(self, verbose: bool = True, unittest: bool = False):
        """
        Initialise the server class by creating an observer object to monitor
        for unity debug log file changes and start main server. Observer and program
        stop once server shuts down.
        """
        self._verbose = verbose
        if not unittest:
            observer = Observer()
            observer.schedule(self, log_path(observer=True), False)
            observer.start()
            self.two_way_handler(5554)
            observer.stop()

    def on_modified(self, event):
        """
        This function will run every time the unity log file is edited/modified in
        any way including when unity decides to update it.

        It will attempt to send the current log file before deleting the contents
        of the local log file. A timed delay will prevent excessive updates at once
        which would cause data loss and other issues to the log file.

        :param event: event instance including file info and type of event
        """

        with open('terminal_log.txt', 'a+') as file:
            print(local_msg['watchdog_update'], file=file, flush=True)

        def send(path):
            with open(path, 'r') as log:
                contents = [line for line in log]
                contents.append('--EOF')
                self.one_way_handler(5555, package=contents)

        if not os.path.exists(event.src_path): return None
        if os.stat(event.src_path).st_size == 0:
            with open('terminal_log.txt', 'a+') as file:
                print(local_msg['stream_complete'], file=file, flush=True)
            self.one_way_handler(5555, f'tg:>')
        else:
            temp: str = 'temp.log'
            temp_name_only: str = 'temp.log'
            for log_name in log_file_names:
                if re.search('[\w]+\.log', event.src_path).group() == log_name:
                    temp = re.sub('[\w]+\.log', f'temp-{log_name}', event.src_path)
                    temp_name_only = f'temp-{log_name}'
            if temp not in log_file_names:
                assert NameError, "No valid unity log files found, please check that the directory " \
                                  "'%LOCALAPPDATA%/Unity/Editor/' exists"
            if self._stream_delay is None:
                shutil.copyfile(event.src_path, temp)
                self._stream_delay = Timer(3, temp_name_only)
                self._stream_delay.start()
            elif os.path.exists(temp) and self._stream_delay.active:
                self._stream_delay.reset()
            elif not os.path.exists(temp) and self._stream_delay.active:
                pass
            elif not os.path.exists(temp) and not self._stream_delay.active:
                shutil.copyfile(event.src_path, temp)
                self._stream_delay = Timer(3, temp_name_only)
                self._stream_delay.start()

    # noinspection PyMethodParameters
    def _connectionBootstrap(func) -> ():
        """
        Wrapper in charge of initialising and stopping a socket correctly
        as well as stopping the server when an event or error occurs such
        as a timeout event.

        :param func: handler function that should extend the wrapper
        """

        # noinspection PyCallingNonCallable
        def _wrapper(self, port: int, sock: socket.socket = None):
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(self._timeout)
                s.bind((self._host, port))
                s.listen()
                try:
                    func(self, port, s)
                except socket.timeout as error:
                    with open('terminal_log.txt', 'a+') as file:
                        print(local_msg['timeout'],
                              end=f'\n\t\t -> {error}\n' if self._verbose else '\n',
                              file=file, flush=True)

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
        with open('terminal_log.txt', 'a+') as file:
            print(local_msg['server_open'], file=file, flush=True)

        while True:
            try:
                # Continuously check for incoming clients waiting for request
                client, address = sock.accept()
                with client:
                    # Continuously check for incoming messages
                    while True:
                        reply = client.recv(self._buffer).decode('utf-8')  # received message
                        if reply:
                            # print unknown command
                            if reply[:4] == 'uc:>':
                                print(reply[4:], flush=True)
                                self.one_way_handler(5555, 'tg:>unity log file empty')
                                break
                            # do nothing if the command is valid. If the command is
                            # 'get log', send it to app
                            elif reply[:4] == 'kc:>':
                                if reply[4:] == 'get log':
                                    log_pth = log_path()
                                    if os.stat(log_pth).st_size == 0:
                                        with open('terminal_log.txt', 'a+') as file:
                                            print(local_msg['stream_complete'], file=file, flush=True)
                                        self.one_way_handler(5555, f'tg:>')
                                        break
                                    with open(log_pth, 'r') as file:
                                        self.one_way_handler(5555, package=[line for line in file])
                                        self.one_way_handler(5555, msg='--EOF')
                                    with open(log_pth, 'w'):
                                        pass
                            continue
                        break
            except (socket.timeout, WindowsError) as error:
                with open('terminal_log.txt', 'a+') as file:
                    print(local_msg['timeout'],
                          f'\n\t\t -> {error}\n' if self._verbose else '\n',
                          file=file, flush=True)
                break
        with open('terminal_log.txt', 'a+') as file:
            print(local_msg['server_closed'], file=file, flush=True)

    def one_way_handler(self, port: int, msg: str = None, package: [str] = None) -> bool:
        """
        Sends a message or an array of messages to application.

        Should be used to receive commands from the app or send the current
        Unity debug log information to the application. Also displays error info.

        :param port: port number
        :param msg: the message (defaults to none)
        :param package: a list of messages (defaults to none)
        """
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.connect((self._host, port))
                # send the message if message not blank
                if msg:
                    sock.send(msg.replace('\t', '').encode('utf-8'))
                    return True
                # send a list of messages if package not blank
                if package:
                    for line in package:
                        sock.send(line.replace('\t', '').encode('utf-8'))
                    sock.send('--EOF'.encode('utf-8'))
                    return True
        except WindowsError as error:
            with open('terminal_log.txt', 'a+') as file:
                print(local_msg['connection_closed'],
                      f'\n\t\t -> {error}' if self._verbose else '\n',
                      file=file, flush=True)
        return False


if __name__ == '__main__':
    t = Terminal()
