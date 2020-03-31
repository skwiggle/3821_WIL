# Run from application on local area network and connect to remote terminal
# will automatically timeout after [--time] minutes
# purposes:
# -   requests log file text from remote terminal
# -   receives messages from terminal
# -   sends messages back to terminal

import os
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
    DATA: [set] = ['app started...']

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
               port: int = 5555, verify: bool = True) -> bool: ...

    def command_lookup(self, command: str) -> str: ...


if __name__ == '__main__':
    client = Client(auto_connect=True, verbose=False)
