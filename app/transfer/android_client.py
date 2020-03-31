# Run from application on local area network and connect to remote terminal
# will automatically timeout after [--time] minutes
# purposes:
# -   requests log file text from remote terminal
# -   receives messages from terminal
# -   sends messages back to terminal

import os
import re
import socket as s
import threading
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
    verbose: bool = False
    current_time = lambda: \
        DT.now().strftime("%I:%M%p")
    update_msg: dict = {
        'success': f'CONSOLE {current_time()}: {os.getlogin()} is now connected to server',
        'failed': f'CLIENT {current_time()}: connection failed, check that the server is running',
        'established': f'CLIENT {current_time()}: a connection has already been established',
        'cmd_success': f'CLIENT {current_time()}: %s',
        'cmd_failed': f'CLIENT {current_time()}: command "%s" failed to send'
    }
    DATA: [set] = [f"--LOG-{DT.today().strftime('%x')}"]

    def __init__(self, auto_connect: bool = False, host: str = 'localhost',
                 port: int = 5555, verbose: bool = False, timeout: int = 3600):
        '''
        initialise host and port variables and then if auto_connect is enabled,
        connect via update()
        '''
        self.HOST = host
        self.PORT = port
        self.verbose = verbose
        if auto_connect:
            update_thr = threading.Thread(target=self.update, args=(timeout, host, 5555))
            command_thr = threading.Thread(target=self.update, args=(timeout, host, 5554, False))
            update_thr.start()
            command_thr.start()

    def update(self, timeout=3600, host: str = 'localhost',
               port: int = 5555, verify: bool = True) -> bool:
        """
        Continuously waits for incoming log info requests or
        server updates from main server, used for both channels;
        log handler and command line handler
        :param host: client hostname (default localhost)
        :param port: connection port number (default 5555)
        :param timeout: duration until timeout (default 1 hour)
        :param verify: should the socket send a verification message (true/false)
        """
        try:
            with s.socket(s.AF_INET, s.SOCK_STREAM) as sock:
                sock.settimeout(timeout)
                sock.connect((host, port))
                if verify:
                    sock.send(bytes(self.update_msg['success'], 'utf-8'))
                with open('./log/temp-log.txt', 'a+') as file:
                    while True:
                        msg = sock.recv(self.BUFFER_SIZE).decode('utf-8')
                        if msg and re.search('(CONSOLE|CLIENT)', msg):
                            print(msg)
                        elif msg:
                            file.write(msg)
                            self.DATA.append(msg)
                        else:
                            return False
        except Exception as e:
            print(self.update_msg['failed'], f'\n\t\t -> {e}' if self.verbose else '')
            return True


if __name__ == '__main__':
    client = Client(auto_connect=True, verbose=False)
