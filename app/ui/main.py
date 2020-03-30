# The main GUI of the application that handles all user
# events, connected to the client.
# Purposes:
#  -    start/close application
#  -    display debug log info
#  -    receive/send user commands
#  -    manually connect to client
#  -    read from temporary log files
import socket

import kivy
from kivy.lang import Builder

kivy.require('1.11.1')

# kivy configuration
from kivy.config import Config

Config.set('graphics', 'width', '480')
Config.set('graphics', 'height', '720')
Config.set('graphics', 'minimum_width', '480')
Config.set('graphics', 'minimum_height', '720')
Config.set('graphics', 'resizable', '1')
Config.set('widgets', 'scroll_moves', '10')

from app.transfer.android_client import Client
from kivymd.app import MDApp
from kivy.uix.recycleview import RecycleView
from kivy.properties import NumericProperty, StringProperty, ListProperty
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.label import MDLabel
from kivy.clock import Clock
import re
from datetime import datetime as DT
import time
import socket as s
import asyncio
import threading


class DebugPanel(RecycleView, Client):

    def log_data(self):
        '''
        filter and append data sent from super class DATA variable over to
        global data variable. This function is called everytime DATA is
        updated whenever a log file is read from the terminal and sent over.
        '''
        self.data = map(lambda x: {'text': str(x)},
                        filter(lambda y: not re.search('(--LOG)+', y),
                               self.DATA))

    def watch_log_update(self):
        '''
        A thread will run this function in the background every second.
        Compare local data value to client DATA variable. If results are
        different and/or aren't empty, copy to local variable and then
        debug screen should automatically update.
        '''
        original = self.DATA
        while True:
            if self.data and (self.data[-1] != original[-1]):
                self.log_data()
                time.sleep(1)

    def __init__(self, **kwargs):
        super(DebugPanel, self).__init__(**kwargs)                  # initialise client super class
        self.data = []                                              # initialise global data variable
        self.log_data()                                             # update global data variable
        watch_conn = threading.Thread(target=self.update)           # create thread as data observer
        watch_log = threading.Thread(target=self.watch_log_update)  # create thread as socket observer
        watch_conn.start()
        watch_log.start()

    def alt_update(self) -> None:
        self.DATA.append(self.get_connection)

    def send_command(self, command) -> str:
        '''
        A non-continuosly property version of the update method that
        returns a message.
        '''
        try:
            with s.socket(s.AF_INET, s.SOCK_STREAM) as sock:
                sock.settimeout(2)
                sock.connect((self.HOST, self.PORT))
                sock.send(bytes(str(command), 'utf-8'))
                return self.update_msg['cmd_success'] % command
        except Exception as e:
            return self.update_msg['cmd_failed']

    @property
    def get_connection(self) -> str:
        '''
        A non-continuosly property version of the update method that
        returns a message.
        '''
        try:
            with s.socket(s.AF_INET, s.SOCK_STREAM) as sock:
                sock.settimeout(2)
                try:
                    sock.connect((self.HOST, self.PORT))
                except Exception as e:
                    return self.update_msg['failed']
                sock.send(bytes(self.update_msg['success'], 'utf-8'))
                recv = sock.recv(self.BUFFER_SIZE).decode('utf-8')
                watch_conn = threading.Thread(target=self.update)
                watch_conn.start()
                return ''
        except Exception as e:
            return self.update_msg['established']

    def update(self, command: str = '') -> bool:
        """
        Continously waits for incoming log info requests or
        server updates from main server
        :param host: client hostname (default localhost)
        :param port: connection port number (default 5555)
        :param timeout: duration until timeout (default 1 hour)
        :param command: string command passed by application
        """
        try:
            with s.socket(s.AF_INET, s.SOCK_STREAM) as sock:
                sock.settimeout(3600)
                sock.connect((self.HOST, self.PORT))
                if command != '':
                    sock.send(bytes(command, 'utf-8'))
                    return True
                sock.send(bytes(self.update_msg['success'], 'utf-8'))
                with open('../transfer/log/temp-log.txt', 'a+') as file:
                    while True:
                        msg = sock.recv(self.BUFFER_SIZE).decode('utf-8')
                        if msg and re.search('(CONSOLE|CLIENT)', msg):
                            self.data.append({'text': str(msg)})
                            self.DATA.append(msg)
                        elif msg:
                            file.write(msg)
                            self.data.append({'text': str(msg)})
                            self.DATA.append(msg)
                        else:
                            return False

        except Exception as e:
            self.data.append({'text': str(self.update_msg['failed'])})
            self.DATA.append(self.update_msg['failed'])
            if self.verbose:
                print(f'\n\t\t -> {e}' if self.verbose else '')
            return True


class DataCell(MDLabel):
    def __init__(self, **kwargs):
        super(DataCell, self).__init__(**kwargs)


class MainApp(MDApp):
    title = "Terminal Genie"
    icon = './icon/app/app_icon256x256.jpg'
    padding_def = NumericProperty(20)
    status = StringProperty('')
    command = StringProperty('')

    def alt_update(self):
        thr = threading.Thread(
            target=self.root.ids['debug_panel'].alt_update)
        thr.start()

    def clear_content(self):
        self.root.ids['debug_panel'].DATA = ['']

    def send_command(self):
        command = self.root.ids['cmd_input'].text
        cmd_thread = threading.Thread(
            target=self.root.ids['debug_panel'].send_command,
            args=(command,))
        cmd_thread.start()

if __name__ == '__main__':
    MainApp().run()
