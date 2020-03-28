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
    client = None
    request_log = False
    current_time = DT.now().strftime("%I:%M%p")
    verification_msg: dict = {
        'client_success': f'CLIENT [{current_time}]: you are now connected to %s (%s)',
        'client_': f'CONSOLE [{current_time}]: client failed to connect',
        'client_left': f'CONSOLE [{current_time}]: client (%s) disconnected from server',
        'log_success': f'CONSOLE [{current_time}]: log finished sending',
        'log_failed': f'CONSOLE [{current_time}]: could not send log'
    }

    def __init__(self, auto_connect=True, port=5555):
        self.port = port
        if auto_connect:
            self.update(port)

    def on_modified(self, event):
        with open(event.src_path, 'r') as file:
            try:
                start_time = time.time()
                print('sending log to client...')
                for line in file:
                    current_time = time.time()
                    self.client.send(bytes(line, 'utf-8'))
                    sys.stdout.write(f'time elapsed: {current_time - start_time}\r')
                    sys.stdout.flush()
                print(self.verification_msg['log_success'])
            except:
                print(self.verification_msg['log_failed'])

    def update(self, port: int, host='localhost') -> None:
        """
        Continuously waits for incoming messages or a 'LOG'
        request from client(s)
        :param port: connection port number (default 5555)
        :param host: hostname (default localhost)
        :param request_log: boolean for if the debug log should be sent to host
        """
        observer = Observer()
        observer.schedule(self, self.debug_info(get_observer_str=True)[0], recursive=True)
        observer.start()
        self.request_log = False
        while True:
            try:
                with s.socket(s.AF_INET, s.SOCK_STREAM) as sock:
                    sock.bind((host, port))
                    sock.listen()
                    self.client, addr = sock.accept()
                    with self.client:
                        self.client.send(bytes(str(self.verification_msg['client_success']) %
                                        (s.gethostbyaddr(addr[0])[0], host), 'utf-8'))
                        while True:
                            reply = self.client.recv(1024)
                            print(reply.decode('utf-8'))
                            if self.request_log:
                                for l in self.debug_info():
                                    print(l)
                                self.request_log = False
                            if not reply:
                                break
            except:
                observer.stop()
                observer.join()
                self.client.close()
                print(self.verification_msg['client_left']
                      % s.gethostbyaddr(addr[0])[0])

    def send_log(self, log: [str]):
        try:
            for line in log:
                self.client.send(bytes(line, 'utf-8'))
        except:
            print(self.verification_msg['log_failed'])

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
    Server(auto_connect=True)
