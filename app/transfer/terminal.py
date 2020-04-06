import socket
import sys
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from app.transfer.server import Server


class Terminal(FileSystemEventHandler, Server):

    def on_modified(self, event):
        with open(self.log_path(), 'r') as file:
            self.one_way_handler(5554, package=[line for line in file])

    def update_action(self, msg: str = None) -> None:
        if msg == 'LOG':
            with open(self.log_path(), 'r') as file:
                self.one_way_handler(5554, package=[line for line in file])
        else:
            print(self.local_msg['command'] % msg)

    @staticmethod
    def log_path(observer: bool = False) -> str:
        """
        Returns the current log file location or the log's parent directory for the
        watchdog observer to monitor for changes.

        :param observer: should the function return the parent directory
                         location instead? (True = yes)
        """
        if 'win' in sys.platform:
            return f"C:/Users/{os.getlogin()}/AppData/Local/Unity/Editor/{'' if observer else 'Editor.log'}"
        elif 'mac' in sys.platform:
            return f"~/Library/Logs/Unity/{'' if observer else 'Editor.log'}"
        elif ('lin' or 'unix') in sys.platform:
            return f"~/.config/unity3d/{'' if observer else 'Editor.log'}"
        raise FileNotFoundError("log path does not exist")