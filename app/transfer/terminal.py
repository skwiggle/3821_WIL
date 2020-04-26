# -*- coding: utf-8 -*-
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
log_file_names: set = {'Editor.log', 'Editor_prev.log', 'upm.log'}
local_msg: dict = {
    'connection_closed': 'failed to send message because no connection was found',
    'timeout': 'connection timed out',
}
logging.basicConfig(
    filemode='a+',
    filename='terminal_log.txt',
    level=logging.DEBUG,
    format='%(levelname)-8s %(asctime)s: %(message)s'
)
logger = logging.getLogger('logger')
error_msg = lambda error, verbose: f'\n\t\t -> {error}' if verbose else ''

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

    def __init__(self, temp_log_name: str, verbose: bool = False):
        self._host = 'localhost'
        self._verbose = verbose
        self.temp_log_name = temp_log_name

    def _one_way_handler(self, port: int, msg: str = None, package: [str] = None) -> bool:
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
            logger.error(local_msg['connection_closed'] % error_msg(error, self._verbose))
        return False

    def clear_temp_log(self) -> bool:
        try:
            temp = f'{log_path(observer=True)}{self.temp_log_name}'
            with open(temp, 'r') as file:
                contents = [line for line in file]
                contents.append('--EOF')
                self._one_way_handler(5555, package=contents)
            os.remove(temp)
            with open(re.sub('temp-', '', log_path(self.temp_log_name)), 'w'):
                pass
            return True
        except Exception as error:
            logger.error(local_msg['timeout'] % error_msg(error, self._verbose))


class Timer(Thread):
    """
    Custom timer that starts and counts down from an (interval) once
    a unity log file has been updated, the counter resets if updated again.

    The class itself does not handle observer and socket objects, it is used
    as only a timer extending a thread object meaning it can only be ran once.
    However, resetting the timer does not complete the thread just as the timer
    reset cannot be ran after the thread has finished.
    """

    def __init__(self, interval: float, temp_log_name: str, verbose: bool = False):
        Thread.__init__(self)
        self._temp_log_name = temp_log_name
        self._current_num = interval
        self._max_num = interval
        self._verbose = verbose
        self.active = False

    def reset(self) -> None:
        """ Reset the timer """
        self._current_num = self._max_num

    def run(self) -> None:
        """ continue to countdown to 0 """
        self.active = True
        sender = IsolatedSender(self._temp_log_name, self._verbose)

        while self._current_num != 0:
            logger.info(f'will send in: {self._current_num} seconds')
            time.sleep(1)
            self._current_num -= 1
        sender.clear_temp_log()
        self.active = False
        logger.info('ready to send log')


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
        self._verbose: bool = False
        # noinspection PyTypeChecker
        self._stream_delay: Timer = None
        self._modifying: bool = False
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
        if self._modifying:
            logger.warning('log file updated while stream was open, will attempt to send afterwards')
            return None
        else:
            self._modifying = True

        with open('terminal_log.txt', 'a+') as file:
            logger.warning('automatic unity log update, sending updated log files...')

        if not os.path.exists(event.src_path):
            logger.error('something went wrong, path from automatic update no longer exists')
            return None

        if os.stat(event.src_path).st_size == 0:
            self.one_way_handler(5555, f'tg:>')
            logger.info('log file sent to client')
        else:
            temp: str = 'temp.log'
            temp_name_only: str = 'temp.log'
            for log_name in log_file_names:
                if re.search('[\w]+\.log', event.src_path).group() == log_name:
                    temp = re.sub('[\w]+\.log', f'temp-{log_name}', event.src_path)
                    temp_name_only = f'temp-{log_name}'
            if temp not in log_file_names:
                logger.critical("No valid unity log files found, please check that the directory "
                                "'%LOCALAPPDATA%/Unity/Editor/' exists")
                exit(-1)
            if self._stream_delay is None:
                shutil.copyfile(event.src_path, temp)
                self._stream_delay = Timer(3, temp_name_only)
                self._stream_delay.start()
                logger.debug('timer started')
            elif os.path.exists(temp) and self._stream_delay.active:
                self._stream_delay.reset()
                logger.debug('timer restarted')
            elif not os.path.exists(temp) and not self._stream_delay.active:
                shutil.copyfile(event.src_path, temp)
                self._stream_delay = Timer(3, temp_name_only)
                self._stream_delay.start()
                logger.debug('timer started')
        self._modifying = False

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
                    logger.critical(local_msg['timeout'] % error_msg(error, self._verbose))
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
                                    logger.info(f'{log_pth} is empty, alerting application')
                                    self.one_way_handler(5555, f'tg:>')
                                    break
                                with open(log_pth, 'r') as file:
                                    logger.info(f'sending contents of {log_pth} to application...')
                                    self.one_way_handler(5555, package=[line for line in file])
                                with open(log_pth, 'w'):
                                    pass
                                logger.debug(f'{log_pth} cleared')
                        logger.debug('message(s) sent')
                        continue
                    break
                break

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
    t = Terminal()
