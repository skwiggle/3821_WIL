import pathlib
import socket
import json
import re


def _ipv4_is_valid(ipv4: str) -> bool:
    """
    Check that IPv4 is valid

    :param ipv4: IPv4 address in the format [0-255].[0-255].[0-255].[0-255]
    """
    if not (isinstance(ipv4, str)) or not \
            re.search('[\d]{1,3}\.[\d]{1,3}\.[\d]{1,3}\.[\d]{1,3}', ipv4):
        return False
    values = re.split('\.', ipv4)
    for value in values:
        if not 0 <= int(value) <= 255:
            return False
    return True

class Settings:
    """Settings Class

    Retrieving and saving settings to a JSON file to maintain continuous
    data between sessions
    """

    _directory: str = './settings.json'     # path to settings.json file
    _settings: dict = {}    # dictionary containing setting's values

    def __init__(self, directory: str):
        """
        check `directory` exists and then assign settings in
        that directory to `_settings`
        """
        if pathlib.Path(directory).exists():
            self._directory = directory
        else:
            # create settings.json if it
            # does not exist
            with open(directory, 'w') as file:
                data = {
                    'host': 'none',
                    'target': 'none',
                    'verbose': True
                }
                json.dump(data, file)
        self.get_settings()

    def get_host(self) -> str:
        """ return Application ipv4 address """
        return self._settings['host']

    def get_target(self) -> str:
        """ return Terminal ipv4 address """
        return self._settings['target']

    def get_verbose(self) -> bool:
        """ return verbose boolean """
        return self._settings['verbose']

    def set_setting(self, key: str, value: str) -> None:
        """ set `_settings` key to value """
        self._settings[key] = value

    def get_settings(self) -> None:
        """ validate and return settings from `_directory` """
        with open(self._directory, 'r') as file:
            data = json.load(file)
            if not _ipv4_is_valid(data['host']):
                data['host'] = 'none'
            if not _ipv4_is_valid(data['target']):
                data['target'] = 'none'
            if not (isinstance(data['verbose'], bool)):
                data['verbose'] = True
        self._settings = data

    def save_settings(self) -> None:
        """ save global settings to `_directory` """
        with open(self._directory, 'w') as file:
            json.dump(self._settings, file)
        return


if __name__ == '__main__':
    settings = Settings('../../settings.json')
    settings.save_settings()
