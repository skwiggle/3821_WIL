# -*- coding: utf-8 -*-
import os
import re
import time
import socket
from threading import Thread
from datetime import datetime as dt
from queue import Queue


class Server:
    """
    A server handler in charge or listening and sending information over sockets

    the class consists of one/two way connection handling as well as allowing for
    custom actions upon event change.
    """
    _host: str = 'localhost'
    _buffer: int = 2048
    _temp_log_folder: str = './log'
    server_active: bool = False
    _stream_active: bool = False
    _timestamp = lambda msg: f'{dt.now().strftime("%I:%M%p")}: {msg}'
    _timeout: float = 3600
    _verbose: bool = False
    scroll_down: bool = False
    DATA: Queue = Queue()
    # noinspection PyArgumentList
    local_msg: dict = {
        'server_open': _timestamp('established server'),
        'server_connect_failed': _timestamp('failed to connect to the server'),
        'server_closed': _timestamp('server closed'),
        'connection_established': _timestamp('connection established'),
        'connection_closed': _timestamp('failed to send message because no connection was found'),
        'timeout': _timestamp('connection timed out'),
        'stream_active': _timestamp('please wait until previous message has sent'),
        'unity_log_empty': _timestamp('unity log file empty')
    }

    def __init__(self, temp_log_folder: str = './log',
                 timeout: float = 3600, verbose: bool = False):
        self._temp_log_folder = temp_log_folder
        self._timeout = timeout
        self._verbose = verbose

    # noinspection PyMethodParameters
    def _connectionBootstrap(func) -> ():
        """
        Wrapper in charge of initialising and stopping a socket correctly
        as well as stopping the server when an event or error occurs such
        as a timeout event.

        :param func: handler function that should extend the wrapper
        """

        # noinspection PyCallingNonCallable,PyUnusedLocal
        def _wrapper(self, port: int, sock: socket.socket = None):
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as ws:
                    ws.settimeout(self._timeout)
                    ws.bind((self._host, port))
                    ws.listen()
                    try:
                        func(self, port, ws)
                    except (socket.timeout, WindowsError) as error:
                        self.DATA.put(self.local_msg['timeout'])
                        if self._verbose:
                            self.DATA.put(f'---> {error}')
                        print(self.local_msg['timeout'],
                              end=f'\n\t\t -> {error}\n' if self._verbose else '\n',
                              flush=True)
            except OSError as error:
                if self._verbose:
                    self.DATA.put(f'---> {error}')

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
        temp_msg: Queue = Queue()
        self.DATA.put(self.local_msg['server_open'])
        print(self.local_msg['server_open'])
        while True:
            try:
                client, address = sock.accept()
                with client:
                    while True:
                        reply = client.recv(self._buffer).decode('utf-8')
                        if reply:
                            if re.search("[\d]{2}:[\d]{2}(AM|PM)", reply):
                                self.DATA.put(reply, block=True)
                                temp_msg.put(reply, block=True)
                            elif reply == 'tg:>':
                                self.DATA.put(self.local_msg['unity_log_empty'], block=True)
                            else:
                                if '--EOF' in reply:
                                    path = f'{self._temp_log_folder}/log-{dt.now().strftime("%d-%m-%Y")}.txt'
                                    if os.path.exists(path):
                                        with open(path, 'a+') as file:
                                            while not temp_msg.empty():
                                                line = temp_msg.get(block=True)
                                                file.write(line)
                                                self.DATA.put(line.replace('\n', ''), block=True)
                                            self.scroll_down = True
                                    else:
                                        with open(path, 'w+') as file:
                                            while not temp_msg.empty():
                                                file.write(temp_msg.get(block=True))
                                            for line in file:
                                                self.DATA.put(line.replace('\n', ''), block=True)
                                else:
                                    temp_msg.put(reply, block=True)
                            continue
                        break
            except WindowsError as error:
                self.DATA.put(self.local_msg['server_connect_failed'], block=True)
                if self._verbose:
                    self.DATA.put(f"---> {error}", block=True)
                print(self.local_msg['server_connect_failed'],
                      f'\n\t\t -> {error}\n' if self._verbose else '\n',
                      flush=True)
                break
        self.DATA.put(self.local_msg['server_connect_failed'], block=True)
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
            # exit function if not msg/package was given
            if not (msg or package):
                return False

            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.connect((self._host, port))
                self._stream_active = True
                if msg:
                    sock.send(msg.encode('utf-8'))
                    self._stream_active = False
                if package:
                    for line in package:
                        sock.send(line.encode('utf-8'))
                    self._stream_active = False
            return True
        except WindowsError as error:
            self.DATA.put(self.local_msg['connection_closed'], block=True)
            if self._verbose:
                self.DATA.put(f"---> {error}", block=True)
            print(self.local_msg['connection_closed'],
                  f'\n\t\t -> {error}' if self._verbose else '\n',
                  flush=True)
        return False

    def test_connection(self, port: int) -> bool:
        """ Test the connection to terminal """
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.setblocking(False)
                sock.settimeout(1)
                sock.connect((self._host, port))
                self.DATA.put(self.local_msg['connection_established'], block=True)
                print(self.local_msg['connection_established'], flush=True)
                return True
        except (WindowsError, socket.timeout) as error:
            self.DATA.put(self.local_msg['server_connect_failed'], block=True)
            if self._verbose:
                self.DATA.put(f"---> {error}", block=True)
            print(self.local_msg['server_connect_failed'],
                  f'\n\t\t -> {error}' if self._verbose else '\n',
                  flush=True)
        return False


if __name__ == '__main__':
    s = Server()
    t1 = Thread(target=s.two_way_handler, args=(1111,))
    t1.start()
    while True:
        s.one_way_handler(1111, '_')
        time.sleep(1)
