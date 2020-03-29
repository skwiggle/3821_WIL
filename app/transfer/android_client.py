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
    """
    Main client class in charge of connecting to and handling incoming/outgoing messages
    from itself and the target terminal. All messages are reconnected back the main
    main application but also act as a communication tool to transfer user commands back
    to the terminal
    """
    HOST, PORT = 'localhost', 5555
    BUFFER_SIZE: int = 2048
    current_time = DT.now().strftime("%I:%M%p")
    verification_msg: dict = {
        'success': f'CONSOLE [{current_time}]: {os.getlogin()} is now connected to server',
        'failed': f'CONSOLE [{current_time}]: connection failed, check that the server is running'
    }

    @property
    def get_connection(self) -> str:
        try:
            with s.socket(s.AF_INET, s.SOCK_STREAM) as sock:
                sock.connect((self.HOST, self.PORT))
                sock.send(bytes(self.verification_msg['success'], 'utf-8'))
                recv = sock.recv(self.BUFFER_SIZE).decode('utf-8')
                return recv
        except:
            return self.verification_msg['failed']

    def __init__(self, auto_connect=False,
                 host='localhost', port=5555):
        self.HOST = host
        self.PORT = port
        if auto_connect:
            while True:
                self.update()
                time.sleep(5)

    def update(self) -> None:
        """
        Continously waits for incoming log info requests or
        server updates from main server
        :param host: client hostname (default localhost)
        :param port: connection port number (default 5555)
        """
        try:
            with s.socket(s.AF_INET, s.SOCK_STREAM) as sock:
                sock.connect((self.HOST, self.PORT))
                sock.send(bytes(self.verification_msg['success'], 'utf-8'))
                with open('./log/temp-log.txt', 'a+') as file:
                    single_line: str = ''
                    while True:
                        msg = sock.recv(self.BUFFER_SIZE).decode('utf-8')
                        if msg and re.search('(CONSOLE|CLIENT) \[', msg):
                            print(msg)
                        elif msg:
                            if re.search('\[[\W\S\D]+\]', msg):
                                single_line += msg
                                file.write(''.join(single_line))
                                single_line = ''
                            else:
                                single_line += msg
                        else:
                            break
        except:
            print(self.verification_msg['failed'])


if __name__ == '__main__':
    client = Client(auto_connect=True)

