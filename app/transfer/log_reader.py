import sys
import os
from _datetime import datetime


class ReadLogFile:

    location: str = None
    _loglocations: dict = {
        'windows': 'C:/Users/%s/AppData/Local/Unity/Editor/Editor.log' %
                   (os.getlogin()),
        'macos': '~/Library/Logs/Unity/Editor.log',
        'linux': '~/.config/unity3d/Editor.log'
    }

    def __init__(self):
        self.check_location_exists()

    def read(self, url: str):
        '''
        read each line of the log file and yield each
        line individually with the current time attached
        :param url: location to log file
        :return: yield a stream of data
        '''
        with open(url, 'r') as file:
            for line in file.readlines():
                yield bytes("[%s]: %s" % (
                      datetime.now().strftime("%m:%H:%m"),
                      line), 'utf-8')


    def check_location_exists(self):
        '''
        Check the debug log file location for each platform
        :return: URL string
        '''
        platform: str = sys.platform
        for pf in self._loglocations.keys():
            if platform.__contains__('win'):
                platform = pf
                break
            if platform.__contains__('mac'):
                platform = pf
                break
            if platform.__contains__('lin'):
                platform = pf
                break
        if os.path.exists(self._loglocations[platform]):
            self.location = self._loglocations[platform]
        else:
            print("File could not be found at \'%s\';\n" %
                   self._loglocations[platform])
            raise FileExistsError




