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
        'server_connect_failed': f'{_timestamp()}: failed to connect to the client',
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
        def _wrapper(self, port: int, sock: socket.socket = None):
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(self._timeout)
                s.bind((self._host, port))
                s.listen()
                print(self.local_msg['server_open'])
                self.DATA.put_nowait(self.local_msg['server_open'])
                try:
                    func(self, port, s)
                except socket.timeout as error:
                    print(self.local_msg['timeout'],
                          f'\n\t\t -> {error}\n' if self._verbose else '\n',
                          flush=True)
                    self.DATA.put(self.local_msg['timeout'])
            self.DATA.put(self.local_msg['server_closed'])
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
        self.server_active = True
        try:
            client, address = sock.accept()
            with client:
                while True:
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
                        self.update_action(msg)
                    continue
        except WindowsError as error:
            print(self.local_msg['server_connect_failed'],
                  f'\n\t\t -> {error}\n' if self._verbose else '\n',
                  flush=True)
            self.DATA.put_nowait(self.local_msg['server_connect_failed'])
            self.DATA.put_nowait(f'---> {error}\n' if self._verbose else '\n',)
        print(self.local_msg['server_closed'])
        self.DATA.put_nowait(self.local_msg['server_closed'])
        self.server_active = False

    def one_way_handler(self, port: int, msg: str = None, package: [str] = None) -> str:
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
                        self.DATA.nowait(line)
                self._stream_active = False
        except WindowsError as error:
            print(self.local_msg['connection_closed'],
                  f'\n\t\t -> {error}\n' if self._verbose else '\n',
                  flush=True)
            self.DATA.put(f"{self.local_msg['connection_closed']}")
            self.DATA.put(f"\t\t -> {error if self._verbose else ''}")
            self._stream_active = False
        return self.local_msg['connection_closed']

    def update_action(self, msg: str = None) -> None:
        """
        The custom action taken once a server receives a message

        :param msg: the message received (which may be any type)
        """
        ...


if __name__ == '__main__':
    s = Server()
    s.one_way_handler(5555, 'hello')
    while not s.DATA.empty():
        print(s.DATA.get_nowait())
    while True:
        continue