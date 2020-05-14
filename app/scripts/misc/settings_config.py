import os
import pathlib
import re
import socket


class Settings:

    _directory: str = './settings_config.txt'
    _settings: dict = {
        'ipv4': '0.0.0.0',
        'verbose': True
    }

    def __init__(self, directory: str):
        if pathlib.Path(directory).exists():
            self._directory = directory
        self.get_settings()

    def get_ipv4(self):
        return self._settings['ipv4'].replace('\n', '')

    def get_verbose(self):
        return self._settings['verbose']

    def set_setting(self, key: str, value: str):
        self._settings[key] = value

    def get_settings(self):
        with open(self._directory, 'r') as file:

            option_ipv4 = re.split('=', file.readline())
            if option_ipv4[0] == 'ipv4' and option_ipv4[1] != ('' or '\n'):
                self._settings['ipv4'] = option_ipv4[1].replace('\n', '')
            else:
                host = socket.gethostname()
                addr = socket.gethostbyname(host)
                self._settings['ipv4'] = addr

            option_verbose = re.split('=', file.readline())
            if option_verbose[0] == 'verbose' and option_verbose[1] != ('' or '\n'):
                if option_verbose[1] == (True or False):
                    self._settings['verbose'] = option_verbose[1]
                else:
                    self._settings['verbose'] = True

    def save_settings(self):
        with open(self._directory, 'w') as file:
            for key, value in self._settings.items():
                file.write(f'{key}={value}\n')


if __name__ == '__main__':
    settings = Settings('../../settings_config.txt')
    settings.save_settings()
