# Run from remote terminal on a local area network and connects
# to android application. Must be run on a machine with Unity
# installed.
# purposes:
# -   Handles connection updates from any client
# -   reads log file and sends data to application
# -   receives messages from application
# -   sends messages to application

import os
import sys
import time
from datetime import datetime as DT
import socket as s


class Server:
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

    HOST, PORT = 'localhost', 5555
    BUFFER_SIZE: int = 2048

    def __init__(self, auto_connect=True,
                 host='localhost', port=5555):
        self.PORT = port
        self.HOST = host
        if auto_connect:
            while True:
                self.update()
                time.sleep(5)

    def update(self) -> None:
        """
        Continuously waits for incoming messages or a 'LOG'
        request from client(s)
        :param port: connection port number (default 5555)
        :param host: hostname (default localhost)
        """
        request_log = False
        with s.socket(s.AF_INET, s.SOCK_STREAM) as sock:
            sock.bind((self.HOST, self.PORT))
            sock.listen()
            client, addr = sock.accept()
            with client:
                current_time = DT.now().strftime("%I:%M%p")
                client.send(bytes("[%s]\tconnected to server: " \
                            "%s (%s)" % (current_time, self.HOST,
                            s.gethostbyaddr(addr[0])[0]), 'utf-8'))
                while True:
                    reply = client.recv(self.BUFFER_SIZE)
                    print(reply.decode('utf-8'))
                    if request_log:
                        for line in self.debug_info():
                            print(line)
                        request_log = False
                    if not reply:
                        break

    def debug_info(self) -> [str]:
        """
        Reads each line of the unity log file depending on the platform.
        """
        platform = sys.platform
        location: str
        current_time = DT.now().strftime("%I:%M%p")

        loglocations: dict = {
            'windows': 'C:/Users/%s/AppData/Local/Unity/Editor/Editor.log' %
                       (os.getlogin()),
            'macos': '~/Library/Logs/Unity/Editor.log',
            'linux': '~/.config/unity3d/Editor.log'
        }

        if platform.__contains__('win'): location = loglocations['windows']
        elif platform.__contains__('mac'): location = loglocations['macos']
        elif platform.__contains__('lin' or 'unix'): location = loglocations['linux']
        else: raise FileNotFoundError

        if os.path.exists(location):
            with open(location, 'r') as log:
                return [f'[{current_time}]\t{line}' for line in log]
        else:
            return ['null']



if __name__ == '__main__':
    Server(auto_connect=True)