# Run from application on local area network and connect to remote terminal
# will automatically timeout after [--time] minutes
# purposes:
# -   requests log file text from remote terminal
# -   receives messages from terminal
# -   sends messages back to terminal

import os
import re
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
    DATA: [set] = ['type ? to see list of commands\n']

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

    def command_lookup(self, command: str, parameters: [str] = ['']) -> str:
        """
        compare command against list of console commands
        """
        command_list = [
            '\n?: get list of commands',
            'get log: request current log from unity'
            'get log --today: get all logs from today',
            'get log --00-01-2000: get all logs from specific day on day-month-year',
            'clear logs: delete all temporary logs',
            'clear log --today: clear all logs from today'
            'clear log --00-01-2000: clear log of specific day',
            '\n'
        ]
        command = command.lower()
        if command[0] == '?':
            for line in command_list:
                self.DATA.append(line)
        if re.search('get log', command):
            return command
        if re.search('get log --today', command):
            try:
                with open(f'./log/log-{DT.now().strftime("%d-%m-%Y")}.txt', 'r+') as file:
                    for line in file:
                        self.DATA.append(line)
                return command
            except:
                return 'no log files exist'
        if re.search('get log --([\d]{2,2}-[\d]{2,2}-[\d]{4,4})', command):
            try:
                with open(f'./log-{parameters[0][2:]}.txt', 'r') as file:
                    for line in file:
                        self.DATA.append(line)
                return command
            except:
                return 'no log file exists on that date'
        if re.search('clear logs', command):
            try:
                for file in os.listdir('./log/'):
                    os.remove(f'.log/{file}')
                return command
            except:
                return 'atleast one log is still being written to, please disconnect from the server first'
        if re.search('clear log --today', command):
            try:
                os.remove(f'./log/log-{DT.now().strftime("%d-%m-%Y")}.txt')
                return 'today\'s log cleared successfully'
            except:
                return 'log still being written to, please disconnect from the server first'
        if re.search('clear log --([\d]{2,2}-[\d]{2,2}-[\d]{4,4})', command):
            try:
                os.remove(f'./log/log-{parameters[0][2:]}.txt')
                return f'log on {parameters[0][2:]} cleared successfully'
            except:
                return 'log still being written to, please disconnect from the server first'
        else:
            return command


if __name__ == '__main__':
    client = Client(auto_connect=True, verbose=False)
