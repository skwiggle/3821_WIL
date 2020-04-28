# -*- coding: utf-8 -*-
import asyncio
import os
import threading
from sys import platform
import logging
import socket

# list of all Unity log files
# noinspection PyArgumentList
log_file_names: list = ['Editor.log', 'Editor-prev.log', 'upm.log']

# List of re-occurring error messages, easily referencable
local_msg: dict = {
    'connection_closed': 'failed to send message because no connection was found%s',
    'timeout': 'connection timed out%s',
    'unknown': 'unknown error, please restart terminal%s'
}

# Configuration of logging system,
# - appends data to 'terminal_log.txt'
# - sets minimal level of error types to DEBUG level
# - sets format of errors to include level, time and message
logging.basicConfig(
    filemode='a+',
    filename='terminal_log.txt',
    level=logging.DEBUG,
    format='%(levelname)-8s %(asctime)s: %(message)s'
)
logger = logging.getLogger('logger')

# lambda function in charge of appending an error message to a logger message
# if `verbose` is True, otherwise, append nothing
error_msg = lambda error, verbose: f'\n\t\t -> {error}' if verbose else ''


def log_path(log_name: str = 'no_file_given', observer: bool = False) -> str:
    """
    Returns the current log file location or the log's parent directory for the
    watchdog observer to monitor for changes.

    :param log_name: name of log file, can be one of the following
                        - Editor.log
                        - Editor-prev.log
                        - upm.log
                     defaults to 'no_file_given'
    :type log_name: str
    :param observer: should the function return the parent directory
                     location instead? (True = yes), defaults to False
    :type observer: bool
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
class Terminal:
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

        :param verbose: Specifies whether or not the error messages should contain
                        the actual system error messages or just errors created by the
                        terminal, defaults to True
        :type verbose: bool
        :param unittest: Used to stop automatically connecting for unit test
                         purposes, defaults to False
        :type unittest: bool
        """
        self._host: str = 'localhost'
        self._buffer: int = 2048
        self._timeout: float = 3600
        self._log_path_dir: str = log_path(observer=True)
        self._is_reading: bool = False
        self._verbose: bool = verbose
        if not unittest:
            """
            observer = Observer()
            observer.schedule(self, log_path(observer=True), False)
            observer.start()
            observer.stop()
            """
            _log_dir_handler = threading.Thread(
                target=self.check_for_updates, daemon=True,
                name='FileHandler')
            _log_dir_handler.start()
            self.two_way_handler(5554)

    def check_for_updates(self):
        """
        Check for file system events within Editor directory of Unity.

        Asynchronously checks for active logs that aren't empty before
        sending name of log to _log_manager()
        """
        _active_logs = set()

        async def _is_empty(_log_name: str):
            """ Check that log file is empty """
            if not os.stat(f'{self._log_path_dir}{_log_name}').st_size == 0:
                _active_logs.add(_log_name)

        async def _update():
            """
            Run _is_empty() asynchronously for each log file in `_active_logs`
            and then perform log operations if at least one file contains content
            """
            await asyncio.gather(
                _is_empty(log_file_names[0]),
                _is_empty(log_file_names[1]),
                _is_empty(log_file_names[2]),
            )
            if len(_active_logs) > 0:
                await self._log_manager(src_files=_active_logs)
            await asyncio.sleep(1)

        while True:
            asyncio.run(_update())
            _active_logs.clear()

    async def _log_manager(self, src_files: {str} = None):
        """
        Extends on_modified function or used whenever 'get log'
        is retrieved.

        This function will attempt to
        -   check for empty log file(s),
        -   send log file(s) if not empty
        -   clear log file(s)

        If any `src_files` are given, only those files will
        be updated.

        :param src_files: Log file, defaults to None
        :type src_files: set
        """
        async def _safeguard(log_name: str):
            """
             Commit main operations of log file interaction

             :param log_name: Name of log file e.g. Editor.log
             :type log_name: str
            """
            path = f'{self._log_path_dir}{log_name}'  # absolute path to log file
            # Check if file is empty
            if os.stat(path).st_size == 0:
                logger.info(f'Unity log file (\'{log_name}\') is empty')
                self.one_way_handler(5555, f'tg:>')
            else:
                # Send contents of file to application
                with open(path, 'r') as log_file:
                    logger.info(f'sending contents of {log_name} to application...')
                    self.one_way_handler(5555, package=[line for line in log_file])
                # Empty file
                with open(path.replace('\\\\', '\\'), 'w'): pass
                logger.info(f'log {log_name} has been cleared')

        # Check, send and clear all log files within the set passed from
        # `_check_for_updates` at once but finish concurrently to avoid
        # issues with data loss
        tasks = (asyncio.create_task(_safeguard(log)) for log in src_files)
        await asyncio.gather(*tasks)

    # noinspection PyMethodParameters
    def _connectionBootstrap(func) -> ():
        """
        Wrapper in charge of initialising and stopping a socket correctly
        as well as stopping the server when an event or error occurs such
        as a timeout event.

        :param func: handler function that extends from `_wrapper`
        :type func: function
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
        :type port: int, optional
        :param sock: parent socket, defaults to None
        :type sock: socket.socket
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
                                print(reply[4:])
                            # do nothing if the command is valid. If the command is
                            # 'get log', send it to app
                            elif reply[:4] == 'kc:>':
                                if reply[4:] == 'get log':
                                    log_pth = log_path(observer=True)
                                    self._log_manager(set(log_file_names))
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
        :type port: int, optional
        :param msg: the message, defaults to None
        :type msg: str
        :param package: a list of messages, defaults to None
        :type port: list
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
                        # limit number of lines to `limit`
                        if index >= 1999: break
                        sock.send(line.replace('\t', '').encode('utf-8'))
                    sock.send('--EOF'.encode('utf-8'))
                    return True
        except WindowsError as error:
            logger.error(local_msg['connection_closed'] % error_msg(error, self._verbose))
        return False


if __name__ == '__main__':
    t = Terminal(verbose=True)
