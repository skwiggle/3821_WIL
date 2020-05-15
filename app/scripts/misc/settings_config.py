import json
import os
import pathlib
import re
import socket

def fix_ipv4() -> str:
    """ Return the IPv4 of this PC and print to log """
    host = socket.gethostname()
    address = socket.gethostbyname(host)
    return address

def _ipv4_is_valid(ipv4: str) -> bool:
    new_ipv4: str = ipv4
    if not (isinstance(ipv4, str)) or not \
            re.search('[\d]{1,3}\.[\d]{1,3}\.[\d]{1,3}\.[\d]{1,3}', ipv4):
        return False
    values = re.split('\.', ipv4)
    for value in values:
        if not 0 <= int(value) <= 255:
            return False
    return True

class Settings:

    _directory: str = './settings.json'
    _settings: dict = {}

    def __init__(self, directory: str):
        """
        check `directory` exists and then assign settings in
        that directory to `_settings`
        """
        if pathlib.Path(directory).exists():
            self._directory = directory
        else:
            with open(directory, 'w') as file:
                data = {
                    'ipv4': fix_ipv4(),
                    'verbose': True
                }
                json.dump(data, file)
        self.get_settings()

    def get_ipv4(self):
        """ return ipv4 address """
        return self._settings['ipv4']

    def get_verbose(self):
        """ return verbose boolean """
        return self._settings['verbose']

    def set_setting(self, key: str, value: str):
        """ set `_settings` key to value """
        self._settings[key] = value

    def get_settings(self):
        """ validate and return settings from `_directory` """
        with open(self._directory, 'r') as file:
            data = json.load(file)
            if not _ipv4_is_valid(data['ipv4']):
                data['ipv4'] = fix_ipv4()
            if not (isinstance(data['verbose'], bool)):
                data['verbose'] = True
        self._settings = data

    def save_settings(self):
        """ save global settings to `_directory` """
        with open(self._directory, 'w') as file:
            json.dump(self._settings, file)
        return


if __name__ == '__main__':
    settings = Settings('../../settings.json')
    settings.save_settings()
