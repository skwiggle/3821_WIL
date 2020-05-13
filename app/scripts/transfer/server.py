#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import time
import socket
from threading import Thread
from datetime import datetime as dt
from queue import Queue
from app.scripts.misc.essentials import local_msg


# noinspection PyArgumentList,PyBroadException
class Server:
    """
    A server handler in charge or listening and sending information over sockets

    the class consists of one/two way connection handling as well as allowing for
    custom actions upon event change.
    """

    def __init__(self, temp_log_folder: str = './scripts/transfer/log',
                 timeout: float = 3600, verbose: bool = False):
        self.host = 'localhost'                            # host ip address (IPv4)
        self._buffer: int = 2048                    # buffer limit (prevent buffer overflow)
        self.scroll_down: bool = False              # checks if app should scroll to the bottom
        self.DATA: Queue = Queue(2000)              # temporary log data storage
        self._temp_log_folder = temp_log_folder     # temporary log directory location
        self.validate_temp_folder()                 # validate the temp log folder exists
        self._timeout = timeout                     # server timeout duration
        self._verbose = verbose                     # checks whether to specify additional error information

    def validate_temp_folder(self):
        """ Make sure the log folder exists, if not, create one"""
        if not os.path.exists(self._temp_log_folder):
            os.mkdir(self._temp_log_folder)

    # noinspection PyMethodParameters
    def _connection_bootstrap(func) -> ():
        """
        Handler function to return wrapper function

        :param func: handler function that extends from :class:`_wrapper`
        :return: wrapper function
        :rtype: function
        """

        # noinspection PyCallingNonCallable,PyUnusedLocal
        def _wrapper(self, port: int, sock: socket.socket = None):
            """
            Wrapper in charge of initialising and stopping a socket correctly
            as well as stopping the server when an event or error occurs such
            as a timeout event.

            :param port: port number
            :type port: int, optional
            :param sock: parent socket, defaults to None
            :type port: socket.socket
            """
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as ws:
                ws.settimeout(self._timeout)
                try:
                    ws.bind((self.host, port))
                    ws.listen()
                    self.DATA.put(local_msg['server_established'])
                    try:
                        func(self, port, ws)
                    except Exception as error:
                        self._append_error(local_msg['unknown'], error)
                except Exception as error:
                    self._append_error(local_msg['server_connect_failed'], "Check the server is on")

        return _wrapper

    # noinspection PyUnusedLocal
    @_connection_bootstrap
    def two_way_handler(self, port: int, sock: socket.socket = None):
        """
        Constantly listen for incoming messages from other hosts.

        Should be used to handle incoming log updates from the terminal
        or incoming commands from the application. Also displays error info.

        :param port: port number
        :type port: int, optional
        :param sock: parent socket, defaults to None
        :type port: socket.socket
        """
        temp_msg: Queue = Queue()   # temporary log data storage

        # Continuously check for incoming clients waiting for request
        while True:
            try:
                # wait for terminal to connect
                client, address = sock.accept()
                with client:
                    # Continuously check for incoming messages
                    while True:
                        reply: str = client.recv(self._buffer).decode('utf-8')
                        # Do something if a viable message is received, otherwise, do nothing
                        if reply:
                            # Send empty log file error message to application if received
                            # message equals 'tg:>'
                            if reply[:4] == 'tg:>':
                                self.DATA.put(local_msg['unity_log_empty'] % reply[4:], block=True)
                            elif reply == 'tga:>':
                                self.DATA.put(local_msg['all_unity_logs_empty'], block=True)
                            else:
                                # When the last line says --EOF, update temporary logs with
                                # `temp_msg` data
                                if '--EOF' in reply:
                                    path = f'{self._temp_log_folder}/log-{dt.now().strftime("%d-%m-%Y")}.txt'
                                    if os.path.exists(path):
                                        with open(path, 'a+') as file:
                                            while not temp_msg.empty():
                                                line = temp_msg.get(block=True)
                                                file.write(line)
                                                if line != '':
                                                    self.DATA.put(line, block=True)
                                            self.scroll_down = True
                                    else:
                                        with open(path, 'w+') as file:
                                            while not temp_msg.empty():
                                                file.write(temp_msg.get(block=True))
                                            for line in file:
                                                self.DATA.put(line.replace('\n', ''), block=True)
                                # Any other message is recognised as log data,
                                # appends to `temp_msg`
                                else:
                                    temp_msg.put(reply, block=True)
                            continue
                        break
            except Exception as error:
                # send an error message to application of error occurs
                self._append_error(local_msg['timeout'], error)

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
                sock.connect((self.host, port))
                # send the message if message not blank
                if msg:
                    sock.send(msg.encode('utf-8'))
                # send a list of messages if package not blank
                if package:
                    for line in package:
                        if line != '':
                            sock.send(line.encode('utf-8'))
            return True
        except Exception as error:
            self._append_error(local_msg['connection_closed'], error)
        return False

    def _append_error(self, error: str, verbose_msg):
        """
        Appends error to application debug panel.

        :param error: custom error message
        :type error: str
        :param verbose_msg: system error message, only appends if
                            `_verbose` is True
        :type verbose_msg: any exception error type
        """
        self.DATA.put(error, block=True)
        if self._verbose:
            self.DATA.put(f"---> {verbose_msg}", block=True)

    # noinspection PyBroadException
    def test_connection(self, port: int) -> bool:
        """ Test the connection to terminal """
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.bind((self.host, port))
        except Exception:
            self._append_error(local_msg['connection_established'], f"Connected to "
                                                                    f"{self.host} on ports {port} and {port+1}")
            return True
        return False


if __name__ == '__main__':
    """ Unit testing only """
    s = Server()
    t1 = Thread(target=s.two_way_handler, args=(1111,))
    t1.start()
    while True:
        s.one_way_handler(1111, '_')
        time.sleep(1)
