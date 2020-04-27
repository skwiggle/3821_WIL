# -*- coding: utf-8 -*-
import asyncio
import os
import shutil
from sys import platform
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from threading import Thread
import logging
import socket
import time
import re

# noinspection PyArgumentList
log_file_names: list = ['Editor.log', 'Editor-prev.log', 'upm.log']
local_msg: dict = {
    'connection_closed': 'failed to send message because no connection was found%s',
    'timeout': 'connection timed out%s',
    'unknown': 'unknown error, please restart terminal%s'
}
logging.basicConfig(
    filemode='a+',
    filename='terminal_log.txt',
    level=logging.DEBUG,
    format='%(levelname)-8s %(asctime)s: %(message)s'
)
logger = logging.getLogger('logger')
error_msg = lambda error, verbose: f'\n\t\t -> {error}' if verbose else ''


def log_path(log_name: str = 'none', observer: bool = False) -> str:
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
        return r'C:\Users\%s\AppData\Local\Unity\Editor\%s' % (os.getlogin(), '' if observer else log_name)
    elif 'mac' in platform:
        return f"~/Library/Logs/Unity/{'' if observer else log_name}"
    elif ('lin' or 'unix') in platform:
        return f"~/.config/unity3d/{'' if observer else log_name}"
    else:
        logger.critical('Path to Unity log files does not exist, check that the one of the following URLs matche that '
                        'of your platform')
        logger.critical(f'WINDOWS    - C:/Users/{os.getlogin()}/AppData/Local/Unity/Editor/')
        logger.critical('MAC OS     - ~/Library/Logs/Unity/')
        logger.critical('LINUX/UNIX - ~/.config/unity3d/')
        exit(-1)


# noinspection PyUnusedLocal
class Terminal(FileSystemEventHandler):
    """
    A server handler in charge or listening and sending information over sockets.
    the class consists of one/two way connection handling and checking for filesystem
    changes for log files.
    """

    def __init__(self, verbose: bool = True, unittest: bool = False):
        """
        Initialise the server class by creating an observer object to monitor
        for unity debug log file changes and start main server. Observer and program
        stop once server shuts down.
        """
        self._host: str = 'localhost'
        self._buffer: int = 2048
        self._timeout: float = 3600
        self._is_reading: bool = False
        self._verbose: bool = verbose
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
        src_dir = re.sub('[\w\d\-]+\.log$', '', event.src_path)     # event source path directory
        src_file = re.search('[\w\d\-]+\.log$', event.src_path).group()     # event source path

        async def _safeguard(log_name: str):
            """
             Commit main operations of log file interaction

             :param log_name: Name of log file e.g. Editor.log
            """
            path = f'{src_dir}{log_name}'   # full path to log file

            # Check if file is empty
            if os.stat(path).st_size == 0:
                logger.info(f'Unity log file (\'{log_name}\') is empty')
                self.one_way_handler(5555, f'tg:>')

            # Send contents of file to application
            with open(path, 'r') as log_file:
                logger.info(f'sending contents of {log_name} to application...')
                self.one_way_handler(5555, package=[line for line in log_file])

            # Empty file
            with open(path.replace('\\\\', '\\'), 'w'): pass
            logger.info(f'log {log_name} has been cleared')

        async def _get_data():
            """
             Check, send and clear all log files at once but finish
             concurrently to avoid concurrency issues
            """
            await asyncio.gather(
                _safeguard(log_file_names[0]),
                _safeguard(log_file_names[1]),
                _safeguard(log_file_names[2]),
            )

        # Run operations if all log files are not empty
        # otherwise, do nothing
        counter: int = 0
        for option in log_file_names:
            if os.stat(f'{src_dir}{option}').st_size == 0:
                counter += 1
        if counter != 3:
            if not self._is_reading:
                self._is_reading = True
                asyncio.run(_get_data())
                self._is_reading = False

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
                logger.info('established server')
                try:
                    func(self, port, s)
                except Exception as error:
                    logger.critical(local_msg['unknown'] % error_msg(error, self._verbose))
            logger.critical('server closed')

        return _wrapper

    # noinspection PyArgumentList
    @_connectionBootstrap
    def two_way_handler(self, port: int, sock: socket.socket = None):
        """
        Constantly listen for incoming messages from other hosts.

        Should be used to handle incoming log updates from the terminal
        or incoming commands from the application. Also displays error info.

        :param port: port number
        :param sock: parent socket
        """

        # Continuously check for incoming clients waiting for request
        while True:
            try:
                client, address = sock.accept()
                with client:
                    # Continuously check for incoming messages
                    while True:
                        reply = client.recv(self._buffer).decode('utf-8')  # received message
                        if reply:
                            # print unknown command
                            if reply[:4] == 'uc:>':
                                self.one_way_handler(5555, 'tg:>unity log file empty')
                                break
                            # do nothing if the command is valid. If the command is
                            # 'get log', send it to app
                            elif reply[:4] == 'kc:>':
                                if reply[4:] == 'get log':
                                    log_pth = log_path()
                                    if os.stat(log_pth).st_size == 0:
                                        logger.warning(f'{log_pth} is empty, alerting application')
                                        self.one_way_handler(5555, f'tg:>')
                                        logger.info('message sent')
                                    else:
                                        with open(log_pth, 'r') as file:
                                            logger.info(f'sending contents of {log_pth} to application...')
                                            self.one_way_handler(5555, package=[line for line in file])
                                            logger.info('package sent')
                                        with open(log_pth, 'w'):
                                            pass
                                        logger.debug(f'{log_pth} cleared')
                                else:
                                    logger.info(f'command executed: \'{reply[4:]}\'')
                            continue
                        break
            except Exception as error:
                logger.error(local_msg['timeout'] % error_msg(error, self._verbose))

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
                    for index, line in enumerate(package):
                        if index >= 1999: break
                        sock.send(line.replace('\t', '').encode('utf-8'))
                    sock.send('--EOF'.encode('utf-8'))
                    return True
        except WindowsError as error:
            logger.error(local_msg['connection_closed'] % error_msg(error, self._verbose))
        return False


if __name__ == '__main__':
    t = Terminal(verbose=True)
