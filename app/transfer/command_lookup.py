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

    def lookup(self, command: str, data: [set]) -> [set]:
        """
        Compare the command against a list of valid commands and execute the command
        and then append an error or success message to the data table.

        :param command: command sent from user input
        :param data: data displayed on the debug screen
        """
        command = command.lower().replace(' ', '')
        if command.lower().replace(' ', '') == 'getlog':
            return data

        parameters = re.split('--', command)
        if parameters[0] == '?':
            for line in self.command_list:
                data.append({'text': line})
        if parameters[0] == 'getlog':
            for line in self.get_log(parameters):
                data.append({'text': line})
        elif parameters[0] == 'clearlog' or parameters[0] == 'clearlogs':
            for line in self.clear_log(parameters):
                data.append({'text': line})
        else:
            data.append({'text': 'unknown command, type ? for a list of commands'})
        return data

    def get_log(self, parameters: [str]) -> [str]:
        """
        Either retrieve a local temporary copy of a log file if it exists or
        request a latest copy from the client terminal's pc. can specify either
        the current day or a specific date.

        :param parameters: the base command followed by parameters
        :param data: data displayed on the debug screen
        """
        data: [str] = []
        if parameters[1] == 'today':
            file_path = f"{self._directory}/log-{dt.now().strftime('%d-%m-%Y')}.txt"
            if os.path.exists(file_path):
                with open(f"{self._directory}/log-{dt.now().strftime('%d-%m-%Y')}.txt", 'r+') as file:
                    for line in file:
                        data.append(line)
            else:
                with open(file_path, 'w'): pass
                data.append('no previous logs from today, blank file created')
        if re.search('[\d]{2,2}(/|-)[\d]{2,2}(/|-)[\d]{4,4}', parameters[1]):
            parameters[1] = re.sub('/', '-', parameters[1])
            file_path = f"{self._directory}/log-{parameters[1]}.txt"
            if os.path.exists(file_path):
                with open(file_path, 'r+') as file:
                    for line in file:
                        data.append(line)
            else:
                with open(file_path, 'w'): pass
                data.append('no previous logs from that day, blank file created')
        else:
            data.append('incorrect date format')
        return data

    def clear_log(self, parameters: [str]) -> [str]:
        """
        Delete a local temporary copy of a log file from the android phone

        :param parameters: the base command followed by parameters
        :param data: data displayed on the debug screen
        """
        data: [str] = []
        if parameters[0] == 'clearlog':
            if parameters[1] == 'today':
                file_path = f"{self._directory}/log-{dt.now().strftime('%d-%m-%Y')}.txt"
                if os.path.exists(file_path):
                    os.remove(file_path)
                    data.append(f'log file at {file_path} deleted')
                else:
                    data.append(f'no log file found')
            if re.search('[\d]{2,2}(/|-)[\d]{2,2}(/|-)[\d]{4,4}', parameters[1]):
                parameters[1] = re.sub('/', '-', parameters[1])
                file_path = f"{self._directory}/log-{parameters[1]}.txt"
                if os.path.exists(file_path):
                    os.remove(file_path)
                    data.append(f'log file at {file_path} deleted')
                else:
                    data.append(f'no log file found')
            else:
                data.append('incorrect date format')
        if parameters[0] == 'clearlogs':
            for file in os.listdir(self._directory):
                os.remove(f'{self._directory}/{file}')
        return data


if __name__ == '__main__':
    c = CommandLookup('./log')
    c.lookup('clear logs', [])

