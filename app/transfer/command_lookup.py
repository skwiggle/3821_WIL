import os
import re
from datetime import datetime as dt


class CommandLookup:

    _directory = './log'
    command_list = [
        '\n?: get list of commands',
        'get log: request current log from unity',
        'get log --today: get all logs from today',
        'get log --00-01-2000: get all logs from specific day on day-month-year',
        'clear logs: delete all temporary logs',
        'clear log --today: clear all logs from today',
        'clear log --00-01-2000: clear log of specific day',
        '\n'
    ]

    def __init__(self, directory: str):
        if os.path.exists(directory):
            if directory[-1] == '/':
                directory[-1] = ''
            self._directory = directory

    def lookup(self, command: str, data: [str]):
        parameters = re.split('--', command.lower().replace(' ', ''))
        if parameters[0] == 'getlog':
            data = self.get_log() if parameters[0] == 'getlog' else data
        elif parameters[0] == 'clearlog':
            data = self.clear_log() if parameters[0] == 'clearlog' else data
        else:
            data.append('unknown command, type ? for a list of commands')
        print(data)
        return data

    def get_log(self, parameters: [str], data: [str]) -> [str]:
        if parameters[1] == 'today':
            file_path = f"{self._directory}/log-{dt.now().strftime('%d-%m-%Y')}.txt"
            if os.path.exists(file_path):
                with open(f"{self._directory}/log-{dt.now().strftime('%d-%m-%Y')}.txt", 'r+') as file:
                    for line in file:
                        data.append(line)
            else:
                with open(file_path, 'w'): pass
                data.append("no previous logs from today, blank file created")
        if re.search('[\d]+(/|-)[\d]+(/|-)[\d]+', parameters[1]):
            re.sub('/', '-', parameters[1], 2)
            file_path = f"{self._directory}/log-{parameters[1]}.txt"
            if os.path.exists(file_path):
                with open(file_path, 'r+') as file:
                    for line in file:
                        data.append(line)
            else:
                with open(file_path, 'w'): pass
                data.append("no previous logs from that day, blank file created")
        return data

    def clear_log(self, parameters: [str], data: [str]):
        if parameters[0] == 'clearlog':
            if parameters[1] == 'today':
                file_path = f"{self._directory}/log-{dt.now().strftime('%d-%m-%Y')}.txt"
                if os.path.exists(file_path):
                    os.remove(file_path)
                    data.append(f'log file at {file_path} deleted')
                else:
                    data.append(f'no log file found')
            if re.search('[\d]+(/|-)[\d]+(/|-)[\d]+', parameters[1]):
                file_path = f"{self._directory}/log-{parameters[1]}.txt"
                if os.path.exists(file_path):
                    os.remove(file_path)
                    data.append(f'log file at {file_path} deleted')
                else:
                    data.append(f'no log file found')
        return data


if __name__ == '__main__':
    c = CommandLookup('./log')
    c.lookup('get bog', [''])

