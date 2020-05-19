#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import enum
import os
from sys import platform
import threading
import asyncio
import socket
import shutil
import logging
import re
import json

# Configuration of logging system,
# - appends data to 'terminal_log.txt'
# - sets minimal level of error types to DEBUG level
# - sets format of errors to include level, time and message
logging.basicConfig(
    filemode='a+',
    filename='./terminal_log.txt',
    level=logging.INFO,
    format='%(levelname)-8s %(asctime)s: %(message)s'
)
logger = logging.getLogger('logger')

# List of re-occurring error messages, easily referencable
local_msg: dict = {
    'server_connect_failed': 'Failed to connect to the server',
    'connection_closed': 'Failed to send message because no connection could be found%s',
    'timeout': 'Connection timed out%s',
    'settings_parse': 'One of the values in settings.json was incorrectly parsed%s',
    'unknown': 'Unknown error, please restart terminal%s'
}

# list of all Unity log files
# noinspection PyArgumentList
log_file_names: tuple = ('Editor.log', 'Editor-prev.log', 'upm.log')

# lambda function in charge of appending an error message to a logger message
# if `verbose` is True, otherwise, append nothing
error_msg = lambda error, verbose: f'\n\t\t -> {error}' if verbose else ''

# A list of key words to filter debug information from unneeded information
_filtered_key_words = {
    "    com.unity.",
    "[INFO] Health Request received",
    "[INFO] Server started on port",
    "[INFO] Starting Server",
    "[LicensingClient]",
    "[Licensing::Module]",
    "[Package Manager]",
    "[Performance]",
    "[Project]",
    "[Subsystems]",
    "[MODES]",
    "[Optix]",
    "[Radeon Pro]",
    "<RI>",
    "ApplyChangesToAssetFolders: ",
    "Assemblies load time: ",
    "Asset Database init time: ",
    "Asset Database refresh time: ",
    "CategorizeAssets: ",
    "CleanLegacyArtifacts: ",
    "CompileScripts: ",
    "Created GICache directory",
    "debugger-agent: ",
    "Deserialize:            ",
    "device created for Microsoft Media Foundation video decoding",
    "EditorUpdateCheck: ",
    "EnsureUptoDateAssetsAreRegisteredWithGuidPM: ",
    "FixTempGuids: ",
    "GatherAllCurrentPrimaryArtifactRevisions: ",
    "GetAllGuidsForCategorization: ",
    "GetLoadedSourceAssetsSnapshot: ",
    "gi::BakeBackendSwitch:",
    "Global illumination init time: ",
    "Hotreload: ",
    "ImportAndPostprocessOutOfDateAssets: ",
    "ImportInProcess: ",
    "ImportManagerImport: ",
    "ImportOutOfProcess: ",
    "InitializeImportedAssetsSnapshot: ",
    "InitializingProgressBar: ",
    "Integration:            ",
    "Integration of assets:  ",
    "InvokeBeforeRefreshCallbacks: ",
    "InvokeProjectHasChanged: ",
    "LoadedImportedAssetsSnapshotReleaseGCHandles: ",
    "Package Manager init time: ",
    "PersistCurrentRevisions: ",
    "PostProcessAllAssetNotificationsAddChangedAssets: ",
    "PostProcessAllAssets: ",
    "Project init time: ",
    "OnDemandSchedulerStart: ",
    "OnSourceAssetsModified: ",
    "Refresh completed in ",
    "RefreshInfo: ",
    "Refreshing native plugins compatible for Editor",
    "RefreshProfiler: ",
    "RemoteAssetCacheDownloadFile: ",
    "RemoteAssetCacheGetArtifact: ",
    "RemoteAssetCacheResolve: ",
    "ReloadImportedAssets: ",
    "ReloadSourceAssets: ",
    "RestoreLoadedAssetsState: ",
    "Scan: ",
    "Scene opening time: ",
    "Services packages init time: ",
    "Template init time: ",
    "Thread Wait Time:       ",
    "Total Operation Time:   ",
    "TrimDiskCacheJob: ",
    "UpdateCategorizedAssets: ",
    "UpdateImportedAssetsSnapshot: ",
    "Unity extensions init time: ",
    "UnloadImportedAssets: ",
    "UnloadStreamsBegin: ",
    "UnloadStreamsEnd: ",
    "UnregisterDeletedAssets: ",
    "Untracked: ",
    "VerifyAssetsAreUpToDateAndCorrect: ",
    "VerifyGuidPMRegistrations: ",
    "WriteModifiedImportersToTextMetaFiles: ",
}

def _get_private_ipv4() -> str:
    """
    Return the IPv4 of this PC and print to log
    NOTE: will return the first IPv4 if multiple IPv4's
          are open
    """
    host = socket.gethostname()
    info = socket.getaddrinfo(host, 5555)
    for ip in info:
        if not ip[0] is socket.AddressFamily.AF_INET6:
            address = ip[4][0]
            read_ip: list = re.split('\.', ip[4][0])
            if read_ip[2] == '0':
                logger.info(f'hosted on: {address} ({host})')
                return address

def _reset_settings() -> dict:
    """ Set settings.json back to default values """
    with open('settings.json', 'w') as output:
        host = _get_private_ipv4()
        data = {
            'host': host,
            'target': host,
            'timeout': 3600,
            'verbose': True
        }
        json.dump(data, output)
    return data


# noinspection PyArgumentList
def _reset_value(value: str) -> None:
    """ Set settings.json back to default values """
    with open('settings.json', 'w') as output:
        data = json.load(output)
        data[value] = _get_private_ipv4()
        json.dump(data)
    return

def startup() -> dict:
    """
    Delete temporary log files that failed to delete from a
    previous session if either the app lost connection too early
    or the terminal closed unexpectedly.

    Load settings from the `settings.json` file into the terminal
    class or create a new settings default class if the former does
    not exist

    These settings include the following properties:
        - ipv4      default to [THIS IP] (IP)   The host IP address (this computer)
        - timeout   default to 3600 (seconds)   The number of seconds before the :class:`Terminal` times out
        - verbose   default to True (boolean)   Specifies whether or not the error messages should contain
                                                the actual system error messages or just errors created by the
                                                terminal, defaults to True

    :returns: global settings dictionary
    """
    parent = log_path(observer=True)

    # make sure that normal unity log files exist and that
    # no temporary logs exist from a previous session
    for option in log_file_names:
        log_pth = f'{parent}{option}'
        temp_log_pth = f'{parent}~{option}'
        if os.path.exists(temp_log_pth):
            os.remove(temp_log_pth)
            logger.warning(f'data from \'{option}\' failed to send to application from previous session, '
                           f'recommended force update')
        if not os.path.exists(log_pth):
            logger.critical(f'Unity log files could not be found at \'{log_pth}\' directory')
            exit(-1)

        # create a new settings.json if one doesn't exist
        # and then return settings dict
        if not os.path.exists('settings.json'):
            _reset_settings()

        # return settings dict
        with open('settings.json', 'r') as settings:
            data = json.load(settings)
            try:
                # check that timeout is a number above 0
                if isinstance(data['host'], str) and isinstance(data['target'], str):
                    if data['host'] == '':
                        _reset_value('host')
                    elif data['target'] == '':
                        _reset_value('target')
                if not (isinstance(data['timeout'], int) and data['timeout'] > 0):
                    logger.error('Timeout must be a number larger than 0, setting it to 3600')
                    data['timeout'] = 3600
                # check that verbose is set to true or false
                if not (isinstance(data['verbose'], bool)):
                    logger.error('Verbose must be set to True or False, setting it to True')
                    data['verbose'] = True
            except Exception as error:
                logger.critical(local_msg['settings_parse'] % error_msg(error, True))
                _reset_settings()

        return data


def log_path(log_name: str = 'no_file_given', observer: bool = False) -> str:
    """
    Returns the current log file location or the log's parent directory for the
    watchdog observer to monitor for changes.

    :param log_name: name of log file, can be one of the following
                        - Editor.log
                        - Editor-prev.log
                        - upm.log
                     defaults to 'no_file_given'
    :param observer: should the function return the parent directory
                     location instead? (True = yes), defaults to False
    """

    new_path: str = ''

    if 'win' in platform:
        new_path = r'C:\Users\%s\AppData\Local\Unity\Editor\%s' % (os.getlogin(), '' if observer else log_name)
    elif 'mac' in platform:
        new_path = "~/Library/Logs/Unity/{'' if observer else log_name}"
    elif ('lin' or 'unix') in platform:
        new_path = f"/home/{os.getlogin()}/.config/unity3d/{'' if observer else log_name}"
    else:
        logger.critical('Path to Unity log files does not exist, check that the one of the following URLs matches that '
                        'of your platform')
        logger.critical(f'WINDOWS    - C:/Users/{os.getlogin()}/AppData/Local/Unity/Editor/')
        logger.critical('MAC OS     - ~/Library/Logs/Unity/')
        logger.critical('LINUX/UNIX - ~/.config/unity3d/')
        exit(-1)

    if not os.path.exists(new_path):
        logger.critical(f'Unity \'Editor\' directory could not be found at {new_path}')
        exit(-1)

    return new_path


# noinspection PyUnusedLocal
class Terminal:
    """
    A server handler in charge or listening and sending information over sockets.
    the class consists of one/two way connection handling and checking for filesystem
    changes for log files.
    """

    settings: dict = None   # settings properties, saved/retrieved from `settings.json`

    def __init__(self, unittest: bool = False):
        """
        Initialise the server class by creating an observer object to monitor
        for unity debug log file changes and start main server. Observer and program
        stop once server shuts down.

        :param unittest: Used to stop automatically connecting for unit test
                         purposes, defaults to False
        """

        self.settings = startup()
        self._buffer: int = 2046                            # buffer limit (prevent buffer overflow)
        self._log_path_dir: str = log_path(observer=True)   # Unity log directory location

        # Open a secondary thread to monitor file system changes
        # to `_log_path_dir` directory
        _log_dir_handler = threading.Thread(
            target=self.check_for_updates, daemon=True,
            name='FileHandler')
        _log_dir_handler.start()

        if not unittest:
            self.two_way_handler()

    def check_for_updates(self, _manual_update: bool = False) -> None:
        """
        Check for file system events within Editor directory of Unity.

        Asynchronously checks for active logs that aren't empty before
        sending name of log to _log_manager()

        :param _manual_update: force the terminal to return all logs, defaults to False
        """

        _active_logs = set()

        async def _is_empty(_log_name: str):
            """ Check that log file is empty """
            if os.stat(f'{self._log_path_dir}{_log_name}').st_size == 0 and _manual_update:
                logger.info(f'Unity log file (\'{_log_name}\') is empty')
                self.one_way_handler(f'tg:>{_log_name}')
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
                _is_empty(log_file_names[2])
            )
            if len(_active_logs) == 0 and _manual_update:
                self.one_way_handler(f'tga:>')
            elif len(_active_logs) > 0:
                await self._log_manager(src_files=_active_logs)
            await asyncio.sleep(5)

        while True:
            if _manual_update:
                asyncio.run(_update())
                break
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
        """

        async def _delay(_log_name: str, _orig_log_len: int = -1):
            print('running delay...')
            """
            Delay the update by 1 second every time the log is modified
            to reduce the chance of data loss
            """
            path = f'{self._log_path_dir}{_log_name}'  # absolute path to log file
            _orig_log_len = os.stat(path).st_size
            while True:
                await asyncio.sleep(10)
                _new_len = os.stat(path).st_size
                if _new_len != _orig_log_len:
                    _orig_log_len = _new_len
                else:
                    break
            return True

        async def _safeguard(_log_name: str) -> None:
            print('running safeguard...')
            """
             Commit main operations of log file interaction

             :param _log_name: Name of log file e.g. Editor.log
            """

            path = f'{self._log_path_dir}{_log_name}'  # absolute path to log file
            temp_path = f'{self._log_path_dir}~{_log_name}'  # absolute path to log file
            shutil.copy(path, temp_path)

        async def _send_log(_log_name: str) -> None:
            print('sending log...')
            """
            Send contents of temporary log to application and then
            delete the file

            :param _log_name: name of log file
            """

            path = f'{self._log_path_dir}{_log_name}'  # absolute path to log file
            temp_path = f'{self._log_path_dir}~{_log_name}'  # absolute path to temporary log file

            # Empty file
            with open(path.replace('\\\\', '\\'), 'w'): pass
            logger.info(f'log {_log_name} has been cleared')

            # Send contents of file to application
            content = []
            with open(temp_path, 'r') as file:
                for line in file:
                    clean_line = re.sub('[\t\r]', '', line)
                    if not any((fline in clean_line) for fline in _filtered_key_words):
                        if clean_line[-1] == '\n':
                            clean_line = clean_line[:-1]
                            print(f'-> {clean_line}')
                        content.append(clean_line)
            await self.async_one_way_handler(package=(x for x in content if x != ''))

            os.remove(temp_path)

        # Check, send and clear all log files within the set passed from
        # :function:`_check_for_updates` at once but finish concurrently to avoid
        # issues with data loss
        delay_tasks = (asyncio.create_task(_delay(src_file)) for src_file in src_files)
        await asyncio.gather(*delay_tasks)

        tasks = (asyncio.create_task(_safeguard(log)) for log in src_files)
        await asyncio.gather(*tasks)

        for log in src_files:
            await asyncio.shield(_send_log(log))

    # noinspection PyMethodParameters
    def _connectionBootstrap(func) -> ():
        """
        Wrapper in charge of initialising and stopping a socket correctly
        as well as stopping the server when an event or error occurs such
        as a timeout event.

        :param func: handler function that extends from `_wrapper`
        """

        # noinspection PyCallingNonCallable
        def _wrapper(self, sock: socket.socket = None):
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                try:
                    s.settimeout(self.settings['timeout'])
                    s.bind((self.settings['host'], 5554))
                    s.listen()
                    logger.info(f'Host address ({self.settings["host"]}:5554) is valid')
                    try:
                        func(self, s)
                    except Exception as error:
                        logger.critical(local_msg['unknown'] % error_msg(error, self.settings['verbose']))
                except Exception as error:
                    logger.critical(local_msg['server_connect_failed'] % error_msg(error, self.settings['verbose']))
            logger.critical('Server closed')

        return _wrapper

    # noinspection PyArgumentList
    @_connectionBootstrap
    def two_way_handler(self, sock: socket.socket = None) -> None:
        """
        Constantly listen for incoming messages from other hosts.

        Should be used to handle incoming log updates from the terminal
        or incoming commands from the application. Also displays error info.

        :param sock: parent socket, defaults to None
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
                                    self.check_for_updates(_manual_update=True)
                                else:
                                    logger.info(f'command executed: \'{reply[4:]}\'')
                            elif reply[:4] == 'tc:>':
                                pass
                            continue
                        break
            except Exception as error:
                logger.error(local_msg['timeout'] % error_msg(error, self.settings['verbose']))
                exit(-1)

    async def async_one_way_handler(self, msg: str = None, package: [str] = None) -> bool:
        """
        Sends a message or an array of messages to application.

        Should be used to receive commands from the app or send the current
        Unity debug log information to the application. Also displays error info.

        :param msg: a message, defaults to None
        :param package: a list of messages, defaults to None
        """
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.connect((self.settings['target'], 5555))
                # send the message if message not blank
                if msg:
                    sock.send(msg.replace('\t', '').encode('utf-8'))
                    return True
                # send a list of messages if package not blank
                if package:
                    for line in package:
                        sock.send(line.encode('utf-8'))
                    sock.send('--EOF'.encode('utf-8'))
            return True
        except Exception as error:
            logger.error(local_msg['connection_closed'] % error_msg(error, self.settings['verbose']))
        return False

    def one_way_handler(self, msg: str = None, package: [str] = None) -> bool:
        """
        Sends a message or an array of messages to application.

        Should be used to receive commands from the app or send the current
        Unity debug log information to the application. Also displays error info.

        :param msg: a message, defaults to None
        :param package: a list of messages, defaults to None
        """
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.connect((self.settings['target'], 5555))
                # send the message if message not blank
                if msg:
                    sock.send(msg.replace('\t', '').encode('utf-8'))
                    return True
                # send a list of messages if package not blank
                if package:
                    for line in package:
                        sock.send(line.encode('utf-8'))
                    sock.send('--EOF'.encode('utf-8'))
            return True
        except Exception as error:
            logger.error(local_msg['connection_closed'] % error_msg(error, self.settings['verbose']))
        return False


if __name__ == '__main__':
    try:
        Terminal()
    except KeyboardInterrupt as end:
        logger.info('Terminal closed\n')
