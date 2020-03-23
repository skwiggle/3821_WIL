# Run from application on local area network and connect to remote terminal
# will automatically timeout after [--time] minutes
# purposes:
# -   requests log file text from remote terminal
# -   receives messages from terminal
# -   sends messages back to terminal

import os
import socket as s
from datetime import datetime as DT


class Client:

    def __init__(self, auto_connect=False,
                 host='localhost', port=5555):
        if auto_connect:
            self.update(host, port)

    def update(self, host: str, port: int) -> None:
        """
        Continously waits for incoming log info requests or
        server updates from main server
        :param host: client hostname (default localhost)
        :param port: connection port number (default 5555)
        """
        with s.socket(s.AF_INET, s.SOCK_STREAM) as sock:
            current_time = DT.now().strftime("%I:%M%p")
            sock.connect((host, port))
            sock.send(bytes(f'[{current_time}]\t{os.getlogin()} is now connected to server\n', 'utf-8'))
            msg = sock.recv(1024).decode('utf-8')
            print(msg)


if __name__ == '__main__':
    Client(auto_connect=True)