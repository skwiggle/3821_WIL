# -*- coding: utf-8 -*-
import os
import re
from datetime import datetime as dt


# noinspection RegExpSingleCharAlternation
class CommandLookup:
    """
     Compares inbound command's format against expected command format
     and returns result to application
     """

    _directory = './log'    # local path to log directory without '/' at end
    command_list = [
        '?: get list of commands',
        'get log: request current log from unity',
        'get log --today: get all logs from today',
        'get log --00-01-2000: get all logs from specific day on day-month-year',
        'clear logs: delete all temporary logs',
        'clear log --today: clear all logs from today',
        'clear log --00-01-2000: clear log of specific day'
    ]

    def __init__(self, _directory: str):
        self._directory = _directory

    def __str__(self):
        return self._directory

    @staticmethod
    def check(command: str) -> bool:
        """
        Do a quick lookup to check if the command exists

        :param command: command string
        :type command: str
        """
        commands = {
            r"\?",
            r"getlog$",
            r"getlog--today$",
            r"getlog--[\d]{2,2}(/|-)[\d]{2,2}(/|-)[\d]{4,4}$",
            r"clearlogs$",
            r"clearlog--today$",
            r"clearlog--[\d]{2,2}(/|-)[\d]{2,2}(/|-)[\d]{4,4}$"
        }
        fixed = command.lower().replace(' ', '')
        for pattern in commands:
            if re.match(pattern, fixed):
                return True
        return False

    def lookup(self, command: str, data: [set]) -> [set]:
        """
         Compare the command against a list of valid commands and execute the command
         and then append an error or success message to the data table.

         :param command: command sent by the user
         :type command: str
         :param data: data displayed on the debug screen
         :type data: list[set]
         :return: new updated version of data information
         :rtype: list[set]
        """
        _timestamp = lambda msg: f'{dt.now().strftime("%I:%M%p")}: {msg}'  # current time

        # command without capitalisation and whitespace
        fixed = command.lower().replace(' ', '')
        """
         filter command must conform to the following cases:
            - first word must be 'clear', 'get' or '?'
            - second word must be 'log' or 'logs'
            - second word is optional
            - third word must be '--today' or '--<date>'
            - third word is optional
            - <date> must have three numbers separated by '/' or '-'
            - day and month must have 2 characters while year has 4
        """
        if re.match('(clear|get|\?)(log|logs)?(--today|--[\d]{2}(/|-)[\d]{2}(/|-)[\d]{4})?$', fixed):
            # return if the command is simply 'get log'
            if fixed == 'getlog':
                return data

            # separate the command from it's parameters
            parameters = re.split('--', f'{fixed}--')
            # return command execution data if viable
            if parameters[0] == '?':
                for line in self.command_list:
                    data.append({'text': line})
            elif parameters[0] == 'getlog':
                for line in self.get_log(parameters):
                    data.append(line)
            elif parameters[0] == 'clearlog' or parameters[0] == 'clearlogs':
                for line in self.clear_log(parameters):
                    data.append(line)
        else:
            # do nothing if the command couldn't find a valid lookup
            data.append({'text': _timestamp(f'\'{command}\'')})

        return data

    def get_log(self, parameters: [str]):
        """
         Either retrieve a local temporary copy of a log file if it exists or
         request a latest copy from the client terminal's pc. can specify either
         the current day or a specific date.

         :param parameters: the base command followed by parameters
         :type parameters: list[str]
        """
        _timestamp = lambda msg: f'{dt.now().strftime("%I:%M%p")}: {msg}'  # current time

        # GET log from TODAY
        if parameters[1] == 'today':
            file_path = f"{self._directory}/log-{dt.now().strftime('%d-%m-%Y')}.txt"
            if os.path.exists(file_path):
                with open(f"{self._directory}/log-{dt.now().strftime('%d-%m-%Y')}.txt", 'r+') as file:
                    for count, line in enumerate(file):
                        if count > 1500: break
                        yield {'text': line}
                yield {'text': _timestamp('end of file----\n')}
            else:
                with open(file_path, 'w'): pass
                yield {'text': _timestamp('no previous logs from today, blank file created')}

        # GET log from SPECIFIC DAY
        elif re.match('[\d]{2}(/|-)[\d]{2}(/|-)[\d]{4}$', parameters[1]):
            parameters[1] = re.sub('/', '-', parameters[1])
            file_path = f"{self._directory}/log-{parameters[1]}.txt"
            if os.path.exists(file_path):
                with open(file_path, 'r+') as file:
                    for count, line in enumerate(file):
                        if count > 1500: break
                        yield {'text': line}
                    yield {'text': _timestamp('end of file----\n')}
            else:
                with open(file_path, 'w'): pass
                yield {'text': _timestamp('no previous logs from that day, blank file created')}

        # return error if parameters were wrong
        else:
            yield {'text': _timestamp('incorrect date format')}

    def clear_log(self, parameters: [str]) -> set:
        """
        Delete a local temporary copy of a log file from the android phone

        :param parameters: the base command followed by parameters
        """
        _timestamp = lambda msg: f'{dt.now().strftime("%I:%M%p")}: {msg}'  # current time
        if parameters[0] == 'clearlog':

            # CLEAR log from TODAY
            if parameters[1] == 'today':
                file_path = f"{self._directory}/log-{dt.now().strftime('%d-%m-%Y')}.txt"
                if os.path.exists(file_path):
                    os.remove(file_path)
                    yield {'text': _timestamp(f'log file at {file_path} deleted')}
                else:
                    yield {'text': _timestamp(f'no log file found at {file_path}')}

            # CLEAR log from SPECIFIC DAY
            elif re.search('[\d]{2}(/|-)[\d]{2}(/|-)[\d]{4}$', parameters[1]):
                parameters[1] = re.sub('/', '-', parameters[1])
                file_path = f"{self._directory}/log-{parameters[1]}.txt"
                if os.path.exists(file_path):
                    os.remove(file_path)
                    yield {'text': _timestamp(f'log file at {file_path} deleted')}
                else:
                    yield {'text': _timestamp(f'no log file found at {file_path}')}

            # return error if date format was wrong
            else:
                yield {'text': _timestamp(f'incorrect date format')}

        # CLEAR all logs
        if parameters[0] == 'clearlogs':
            for file in os.listdir(self._directory):
                os.remove(f'{self._directory}/{file}')
            yield {'text': _timestamp('all log files deleted')}


if __name__ == '__main__':
    c = CommandLookup('./log')
    print(c.check('get log--01/02-2090'))
