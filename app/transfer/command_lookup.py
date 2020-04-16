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

    def __str__(self):
        return self._directory

    def lookup(self, command: str, data: [set]) -> [set]:
        """
        Compare the command against a list of valid commands and execute the command
        and then append an error or success message to the data table.

        :param command: command sent from user input
        :param data: data displayed on the debug screen
        """
        _timestamp = lambda: dt.now().strftime("%I:%M%p")   # current time
        # command without capitalisation, whitespace and special characters except '?', '/' and '-'
        command_fixed = re.sub('[^\?\-\/a-zA-Z0-9]+', '', command.lower().replace(' ', ''))
        print(command_fixed)
        # return if the command is simply 'get log'
        if command_fixed == 'getlog':
            return data

        # seperate the command from it's parameters
        parameters = re.split('--', command_fixed)
        if parameters[0] == '?':
            for line in self.command_list:
                data.append({'text': line})
        elif parameters[0] == 'getlog':
            for line in self.get_log(parameters):
                data.append(line)
            print(data)
        elif parameters[0] == 'clearlog' or parameters[0] == 'clearlogs':
            for line in self.clear_log(parameters):
                data.append(line)
        else:
            # do nothing if the command couldn't find a valid lookup
            data.append({'text': f'{_timestamp()}: \'{command}\''})
        return data

    def get_log(self, parameters: [str]):
        """
        Either retrieve a local temporary copy of a log file if it exists or
        request a latest copy from the client terminal's pc. can specify either
        the current day or a specific date.

        :param parameters: the base command followed by parameters
        """
        _timestamp = lambda: dt.now().strftime("%I:%M%p")   # current time

        # GET log from TODAY
        if parameters[1] == 'today':
            file_path = f"{self._directory}/log-{dt.now().strftime('%d-%m-%Y')}.txt"
            if os.path.exists(file_path):
                with open(f"{self._directory}/log-{dt.now().strftime('%d-%m-%Y')}.txt", 'r+') as file:
                    for line in file:
                        yield {'text': line}
                yield {'text': f'\n{_timestamp()}: end of file----\n'}
            else:
                with open(file_path, 'w'): pass
                yield {'text': f'{_timestamp()}: no previous logs from today, blank file created'}
        # GET log from SPECIFIC DAY
        elif re.match('[\d]{2,2}(/|-)[\d]{2,2}(/|-)[\d]{4,4}$', parameters[1]):
            parameters[1] = re.sub('/', '-', parameters[1])
            file_path = f"{self._directory}/log-{parameters[1]}.txt"
            if os.path.exists(file_path):
                with open(file_path, 'r+') as file:
                    for line in file:
                        yield {'text': line}
                    yield {'text': f'\n{_timestamp()}: end of file----\n'}
            else:
                with open(file_path, 'w'): pass
                yield {'text': f'{_timestamp()}: no previous logs from that day, blank file created'}
        else:
            # return error if parameters were wrong
            yield {'text': f'{_timestamp()}: incorrect date format'}

    def clear_log(self, parameters: [str]):
        """
        Delete a local temporary copy of a log file from the android phone

        :param parameters: the base command followed by parameters
        """
        _timestamp = lambda: dt.now().strftime("%I:%M%p")
        data: [str] = []
        if parameters[0] == 'clearlog':
            # CLEAR log from TODAY
            if parameters[1] == 'today':
                file_path = f"{self._directory}/log-{dt.now().strftime('%d-%m-%Y')}.txt"
                if os.path.exists(file_path):
                    os.remove(file_path)
                    yield {'text': f'{_timestamp()}: log file at {file_path} deleted'}
                else:
                    yield {'text': f'{_timestamp()}: no log file found at {file_path}'}
            # CLEAR log from SPECIFIC DAY
            elif re.search('[\d]{2,2}(/|-)[\d]{2,2}(/|-)[\d]{4,4}$', parameters[1]):
                parameters[1] = re.sub('/', '-', parameters[1])
                file_path = f"{self._directory}/log-{parameters[1]}.txt"
                if os.path.exists(file_path):
                    os.remove(file_path)
                    yield {'text': f'{_timestamp()}: log file at {file_path} deleted'}
                else:
                    yield {'text': f'{_timestamp()}: no log file found at {file_path}'}
            else:
                # return error if parameters were wrong
                yield {'text': f'{_timestamp()}: incorrect date format'}
        # CLEAR all logs
        if parameters[0] == 'clearlogs':
            for file in os.listdir(self._directory):
                os.remove(f'{self._directory}/{file}')
            yield {'text': f'{_timestamp()}: all log files deleted'}
        # return updated data
        return data


if __name__ == '__main__':
    c = CommandLookup('./log')
    print(c.lookup('clear log --today', []))
