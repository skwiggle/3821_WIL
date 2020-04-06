# -*- coding: utf-8 -*-
import os
import re
import time
from sys import stderr, stdout, platform
import socket
from threading import Thread
from datetime import datetime as dt
from typing import Iterable


class Server:
    """
    A server handler in charge or listening and sending information over sockets

    the class consists of one/two way connection handling as well as allowing for
    custom actions upon event change.
    """
    _host: str = 'localhost'
    _buffer: int = 2048
    _stream_active: bool = False
    _timestamp = lambda: dt.now().strftime("%I:%M%p")
    _timeout: float = 3600
    _verbose: bool = False
    data: [str] = ['type ? for a list of commands']
    local_msg: dict = {
        'server_open': f'{_timestamp()}: established server',
        'server_closed': f'{_timestamp()}: server closed',
        'connection_closed': f'{_timestamp()}: failed to send message because no connection was found',
        'timeout': f'{_timestamp()}: connection timed out'
    }

    def _connectionBootstrap(func) -> ():
        def _wrapper(self, port: int, sock: socket.socket = None):
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(self._timeout)
                s.bind((self._host, port))
                s.listen()
                try:
                    func(self, port, s)
                except socket.timeout as error:
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
        while True:
            try:
                client, address = sock.accept()
                with client:
                    print(self.local_msg['server_open'])
                    msg = client.recv(self._buffer).decode('utf-8')
                    print(msg)
                    if msg:
                        self.update_action(msg)
                    continue
            except WindowsError as error:
                print(self.local_msg['server_closed'],
                      end=f'\n\t\t -> {error}\n' if self._verbose else '\n',
                      flush=True)
                break
        print(self.local_msg['closed'])
        exit(0)

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
                self._stream_active = False
        except WindowsError as error:
            print(self.local_msg['connection_closed'],
                  end=f'\n\t\t -> {error}\n' if self._verbose else '\n',
                  flush=True)
            self._stream_active = False

    def update_action(self, msg: str = None) -> None:
        """
        The custom action taken once a server receives a message

        :param msg: the message received
        """
        ...


if __name__ == '__main__':
    s = Server()
    t1 = Thread(target=s.two_way_handler, args=(5555, 'log'))
    t2 = Thread(target=s.one_way_handler, args=(5555, 'hello'))
    t1.start()
    t2.start()
    t1.join()
    t2.join()