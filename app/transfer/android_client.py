# Run from application on local area network and connect to remote terminal
# will automatically timeout after [--time] minutes
# purposes:
# -   requests log file text from remote terminal
# -   receives messages from terminal
# -   sends messages back to terminal

import os
import re
import socket as s
import time
from datetime import datetime as DT


class Client:

    HOST, PORT = 'localhost', 5555
    BUFFER_SIZE: int = 2048

    def __init__(self, auto_connect=False,
                 host='localhost', port=5555):
        self.HOST = host
        self.PORT = port
        if auto_connect:
            while True:
                self.update()
                time.sleep(2)

    def update(self) -> str:
        """
        Continously waits for incoming log info requests or
        server updates from main server
        :param host: client hostname (default localhost)
        :param port: connection port number (default 5555)
        """
        full_msg: str = ''
        try:
            with s.socket(s.AF_INET, s.SOCK_STREAM) as sock:
                current_time = DT.now().strftime("%I:%M%p")
                sock.connect((self.HOST, self.PORT))
                sock.send(bytes(f'CONSOLE [{current_time}]: {os.getlogin()} is now connected to server\n', 'utf-8'))
                while True:
                    msg = sock.recv(self.BUFFER_SIZE).decode('utf-8')
                    print(msg)
                    if not msg:
                        break
        except:
            return f"CONSOLE [{current_time}]: connection failed, check that the server is running"

    def send_cmd(self, command: str):
        current_time = DT.now().strftime("%I:%M%p")
        try:
            with s.socket(s.AF_INET, s.SOCK_STREAM) as sock:
                sock.connect((self.HOST, self.PORT))
                try:
                    sock.send(b'{command}')
                except:
                    sock.close()
                    return "command failed to send, try again"
                finally:
                    sock.close()
                    return f"sent -> '{command}'"
        except:
            return f"CONSOLE [{current_time}]: connection failed, check that the server is running"


if __name__ == '__main__':
    Client(auto_connect=True)
