# -*- coding: utf-8 -*-
import os
import re
import time
from sys import stderr, stdout, platform
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
    _timestamp = lambda: dt.now().strftime("%I:%M%p")
    _timeout: float = 3600
    _verbose: bool = False
    DATA: Queue = Queue()
    local_msg: dict = {
        'server_open': f'{_timestamp()}: established server',
        'server_connect_failed': f'{_timestamp()}: failed to connect to the server',
        'server_closed': f'{_timestamp()}: server closed',
        'connection_closed': f'{_timestamp()}: failed to send message because no connection was found',
        'timeout': f'{_timestamp()}: connection timed out',
        'stream_active': f'{_timestamp()}: please wait until previous message has sent'
    }

    def __init__(self, temp_log_folder: str = './log',
                 timeout: float = 3600, verbose: bool = False):
        self._temp_log_folder = temp_log_folder
        self._timeout = timeout
        self._verbose = verbose

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
                self.DATA.put(self.local_msg['server_open'])
                print(self.local_msg['server_open'])
                try:
                    func(self, port, s)
                except socket.timeout as error:
                    self.DATA.put(self.local_msg['timeout'])
                    if self._verbose:
                        self.DATA.put(f'---> {error}')
                    print(self.local_msg['timeout'],
                          end=f'\n\t\t -> {error}\n' if self._verbose else '\n',
                          flush=True)
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
        while True:
            try:
                client, address = sock.accept()
                with client:
                    while True:
                        reply = client.recv(self._buffer).decode('utf-8')
                        if reply:
                            if re.search('\[[\d]{2,2}:[\d]{2,2}(AM|PM)', reply):
                                self.DATA.put(reply, block=True)
                                temp_msg.put(f'{reply}\n', block=True)
                            else:
                                if reply == '--EOF':
                                    path = f'{self._temp_log_folder}/log-{dt.now().strftime("%d-%m-%Y")}.txt'
                                    if os.path.exists(path):
                                        with open(path, 'a+') as file:
                                            while not temp_msg.empty():
                                                file.write(temp_msg.get(block=True))
                                            for line in file:
                                                self.DATA.put(line, block=True)
                                    else:
                                        with open(path, 'w+') as file:
                                            while not temp_msg.empty():
                                                file.write(temp_msg.get(block=True))
                                            for line in file:
                                                self.DATA.put(line, block=True)
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
        except WindowsError as error:
            self.DATA.put(self.local_msg['connection_closed'], block=True)
            if self._verbose:
                self.DATA.put(f"---> {error}", block=True)
            print(self.local_msg['connection_closed'],
                  f'\n\t\t -> {error}' if self._verbose else '\n',
                  flush=True)
        self._stream_active = False

    def test_connection(self, port: int) -> bool:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.setblocking(False)
                sock.settimeout(1)
                sock.connect((self._host, port))
                return True
        except (WindowsError, socket.timeout) as error:
            self.DATA.put(self.local_msg['server_connect_failed'], block=True)
            if self._verbose:
                self.DATA.put(f"---> {error}", block=True)
            print(self.local_msg['server_connect_failed'],
                  f'\n\t\t -> {error}' if self._verbose else '\n',
                  flush=True)
        return False
'''
    def _connectionBootstrap(func) -> ():
        def _wrapper(self, port: int, sock: socket.socket = None):
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(self._timeout)
                s.bind((self._host, port))
                s.listen()
                try:
                    self.server_active = True
                    print(self.local_msg['server_open'])
                    self.DATA.put_nowait(self.local_msg['server_open'])
                    func(self, port, s)
                    self.server_active = False
                except Exception as error:
                    print(self.local_msg['timeout'],
                          f'\n\t\t -> {error}\n' if self._verbose else '\n',
                          flush=True)
                    self.DATA.put_nowait(self.local_msg['timeout'])
            self.DATA.put_nowait(self.local_msg['server_closed'])
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
        temp_msg: str = ''
        while True:
            try:
                client, address = sock.accept()
                with client:
                    msg = client.recv(self._buffer).decode('utf-8')
                    if msg:
                        if msg == 'EOF':
                            path = f'{self._temp_log_folder}/log-{dt.now().strftime("%d-%m-%Y")}.txt'
                            if os.path.exists(path):
                                with open(path, 'a+') as file:
                                    file.write(temp_msg)
                            else:
                                with open(path, 'w+') as file:
                                    file.write(temp_msg)
                        temp_msg += msg
                    if msg:
                        print(msg.decode('utf-8'))
                    continue
            except WindowsError as error:
                print(self.local_msg['server_connect_failed'],
                      f'\n\t\t -> {error}\n' if self._verbose else '\n',
                      flush=True)
                self.DATA.put_nowait(self.local_msg['server_connect_failed'])
                self.DATA.put_nowait(f'---> {error}\n' if self._verbose else '\n',)
        print(self.local_msg['server_closed'])
        self.DATA.put_nowait(self.local_msg['server_closed'])

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
                        self.DATA.put_nowait(line)
                self._stream_active = False
        except WindowsError as error:
            print(self.local_msg['connection_closed'],
                  f'\n\t\t -> {error}\n' if self._verbose else '\n',
                  flush=True)
            self.DATA.put_nowait(f"{self.local_msg['connection_closed']}\n---> {error if self._verbose else ''}")
        self._stream_active = False
        # self.DATA.put_nowait(f"{self._timestamp}: '{msg}' sent")

    def test_connection(self, port: int) -> bool:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.setblocking(False)
                sock.settimeout(1)
                sock.connect((self._host, port))
                return True
        except (WindowsError, socket.timeout) as error:
            self.DATA.put_nowait(f"{self.local_msg['server_connect_failed']}\n---> {error if self._verbose else ''}")
        return False

    def update_action(self, msg: str = None) -> None:
        """
        The custom action taken once a server receives a message

        :param msg: the message received (which may be any type)
        """
        ...
'''


if __name__ == '__main__':
    s = Server()
