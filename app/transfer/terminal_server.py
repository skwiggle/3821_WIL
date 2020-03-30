# Run from remote terminal on a local area network and connects
# to android application. Must be run on a machine with Unity
# installed.
# purposes:
# -   Handles connection updates from any client
# -   reads log file and sends data to application
# -   receives messages from application
# -   sends messages to application

import os
import re
import sys
import watchdog
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from datetime import datetime as DT
import socket as s
import time


class Server(FileSystemEventHandler):
    """
    Run from remote terminal on a local area network and connects
    to android application. Must be run on a machine with Unity
    installed.
    purposes:
    -   Handles connection updates from any client
    -   reads log file and sends data to application
    -   receives messages from application
    -   sends messages to application
    """
    client = None                       # active client object
    request_log: bool = False           # send log over to application true/false
    HOST, PORT = 'localhost', 5555      # default hostname and port number
    BUFFERSIZE: int = 2048              # message size limit
    verbose: bool = False               # display exception error true/false
    log_location: str = ''              # location of log file
    current_time = lambda: \
        DT.now().strftime("%I:%M%p")    # returns the current time

    # list of all custom error messages
    update_msg: dict = {
        'client_success': f'CLIENT {current_time()}: you are now connected to %s (%s)',
        'client_failed': f'CONSOLE {current_time()}: client failed to connect',
        'client_left': f'CONSOLE {current_time()}: client (%s) disconnected from server',
        'log_not_found': f'CONSOLE {current_time}: no log file found at \'%s\'',
        'log_success': f'CONSOLE {current_time()}: log finished sending',
        'log_failed': f'CONSOLE {current_time()}: could not send log',
        'instance': f'CONSOLE {current_time()}: A terminal instance is already running'
    }

    def __init__(self, auto_connect=True, host='localhost',
                 port=5555, verbose=False):
        self.HOST = host
        self.PORT = port
        self.verbose = verbose
        if auto_connect:
            self.update(port)

    def on_modified(self, event):
        """
        if unity log file is modified aka. contents are overwritten, open and
        copy the contents and then send it to the application
        """
        with open(event.src_path, 'r') as file:
            try:
                start_time = time.time()
                print('log file was updated, sending log to client...')
                for line in file:
                    current_time = time.time()
                    self.client.send(bytes(line, 'utf-8'))
                    sys.stdout.write(f'time elapsed: {current_time - start_time}\r')
                    sys.stdout.flush()
                print(self.update_msg['log_success'])
            except Exception as e:
                print(self.update_msg['log_failed'], f'\n\t\t -> {e}' if self.verbose else '')

    def update(self, port: int, host='localhost') -> None:
        """
        Continuously waits for incoming messages or a 'LOG'
        request from client(s)
        :param port: connection port number (default 5555)
        :param host: hostname (default localhost)
        :param request_log: boolean for if the debug log should be sent to host
        """
        try:
            observer = Observer()
            self.log_location = self.debug_info(get_observer_str=True)[0]
            observer.schedule(self, self.log_location, recursive=True)
            observer.start()
            self.request_log = False
        except Exception as e:
            print(self.update_msg['log_not_found'], f'\n\t\t -> {e}' if self.verbose else '')
        while True:
            try:
                with s.socket(s.AF_INET, s.SOCK_STREAM) as sock:
                    try:
                        sock.bind((self.HOST, self.PORT))
                        sock.listen()
                    except:
                        print(self.update_msg['instance'])
                        exit(-1)
                    try:
                        self.client, addr = sock.accept()
                        with self.client:
                            self.client.settimeout(600)
                            self.client.send(bytes(str(self.update_msg['client_success']) %
                                                   (s.gethostbyaddr(addr[0])[0], host), 'utf-8'))
                            while True:
                                reply = self.client.recv(self.BUFFERSIZE)
                                print(reply.decode('utf-8'))
                                if self.request_log:
                                    for line in self.debug_info():
                                        print(line)
                                    self.request_log = False
                                if not reply:
                                    break
                    except Exception as e:
                        print(self.update_msg['client_left'] % (s.gethostbyaddr(addr[0])[0]),
                              f'\n\t\t -> {e}' if self.verbose else '')
            except Exception as e:
                observer.stop()
                observer.join()
                self.client.close()
                print(self.update_msg['client_left'] % s.gethostbyaddr(addr[0])[0],
                      f'\n\t\t -> {e}' if self.verbose else '')

    def send_log(self, log: [str]):
        try:
            for line in log:
                self.client.send(bytes(line, 'utf-8'))
            self.client.send(b'--EOF')
        except Exception as e:
            print(self.update_msg['log_failed'],
                  f'\n\t\t -> {e}' if self.verbose else '')

    @staticmethod
    def debug_info(url="", get_observer_str=False) -> [str]:
        """
        Reads each line of the unity log file depending on the platform.
        """
        platform = sys.platform
        location: str
        current_time = DT.now().strftime("%I:%M%p")

        def return_lines(abs_url: str):
            if os.path.exists(location):
                with open(abs_url, 'r') as log:
                    return [f'[{current_time}]\t{line}' for line in log]
            else:
                return ['null']

        if url != "":
            return_lines(url)

        loglocations: dict = {
            'windows': 'C:/Users/%s/AppData/Local/Unity/Editor/Editor.log' %
                       (os.getlogin()),
            'macos': '~/Library/Logs/Unity/Editor.log',
            'linux': '~/.config/unity3d/Editor.log'
        }

        if platform.__contains__('win'):
            location = loglocations['windows']
        elif platform.__contains__('mac'):
            location = loglocations['macos']
        elif platform.__contains__('lin' or 'unix'):
            location = loglocations['linux']
        else:
            raise FileNotFoundError

        if get_observer_str:
            return [re.sub('[\w\d]+.log', '', location)]
        return_lines(location)


if __name__ == '__main__':
    server = Server(auto_connect=True, verbose=True)
