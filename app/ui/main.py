# The main GUI of the application that handles all user
# events, connected to the client.
# Purposes:
#  -    start/close application
#  -    display debug log info
#  -    receive/send user commands
#  -    manually connect to client
#  -    read from temporary log files
import os

import kivy
kivy.require('1.11.1')

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
from kivy.properties import NumericProperty, StringProperty
from kivymd.uix.label import MDLabel
import re
import time
import socket as s
from datetime import datetime as DT
import threading


class DebugPanel(RecycleView, Client):

    def __init__(self, **kwargs):
        super(DebugPanel, self).__init__(**kwargs)  # initialise client super class
        self.data = []  # initialise global data variable
        update_thr = threading.Thread(target=self.update)
        watch_log = threading.Thread(target=self.watch_log_update)  # create thread as data observer
        watch_log.start()
        update_thr.start()
        try:
            with open(f'../transfer/log/log-%s.txt' % DT.now().strftime("%d-%m-%Y"), 'x') as file:
                file.write('\n')
        except:
            pass

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
                self.data = map(lambda x: {'text': str(x)}, self.DATA)
                time.sleep(0.25)

    def alt_update(self, command: str = None) -> None:
        """
        Alternate update request, request a continuous log handler socket connection
        to terminal if the current socket ended, else, do nothing.
        OR: Send a command to terminal host
        """
        if command is None:
            self.DATA.append(self.get_connection)
        else:
            parameters = re.findall('--[\S]+[\s]?', command)
            command = self.command_lookup(command, parameters)
            result = self.send_command(5554, command)
            self.DATA.append(result)

    def command_lookup(self, command: str, parameters) -> str:
        """
        compare command against list of console commands
        """
        command_list = [
            '\n?: get list of commands',
            'get log: request current log from unity'
            'get log --today: get all logs from today',
            'get log --00-01-2000: get all logs from specific day on day-month-year',
            'clear logs: delete all temporary logs',
            'clear log --today: clear all logs from today'
            'clear log --00-01-2000: clear log of specific day',
            '\n'
        ]
        command = command.lower()
        if command[0] == '?':
            for line in command_list:
                self.DATA.append(line)
        if re.search('get logs', command):
            return command
        if re.search('get log --today', command):
            try:
                with open(f'../transfer/log/log-{DT.now().strftime("%d-%m-%Y")}.txt', 'r+') as file:
                    for line in file:
                        self.DATA.append(line)
                return command
            except:
                return 'no log files exist'
        if re.search('get log --([\d]{2,2}-[\d]{2,2}-[\d]{4,4})', command):
            try:
                with open(f'../transfer/log/log-{parameters[0][2:]}.txt', 'r') as file:
                    for line in file:
                        self.DATA.append(line)
                return command
            except:
                return 'no log file exists on that date'
        if re.search('clear logs', command):
            try:
                for file in os.listdir('../transfer/log/'):
                    os.remove(f'../transfer/log/{file}')
                return command
            except:
                return 'logs could not be deleted, directory may be empty'
        if re.search('clear log --today', command):
            try:
                os.remove(f'../transfer/log/log-{DT.now().strftime("%d-%m-%Y")}.txt')
                return command
            except:
                return 'log could not be removed because it does not exist'
        if re.search('clear log --([\d]{2,2}-[\d]{2,2}-[\d]{4,4})', command):
            try:
                os.remove(f'../transfer/log/log-{parameters[0][2:]}.txt')
                return command
            except:
                return 'log could not be removed because it does not exist'
        else:
            return 'unknown command, type ? to see list of commands'



    def send_command(self, port: int, command: str) -> str:
        '''
        A non-continuosly property version of the update method that
        returns a message.
        '''
        try:
            with s.socket(s.AF_INET, s.SOCK_STREAM) as sock:
                sock.settimeout(2)
                sock.connect((self.HOST, port))
                sock.send(bytes(self.update_msg['cmd_success'] % command, 'utf-8'))
                time.sleep(0.25)
                return self.update_msg['cmd_success'] % command
        except:
            return self.update_msg['cmd_failed'] % command

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
                log_handler = threading.Thread(target=self.update)
                log_handler.start()
                return ''
        except Exception as e:
            return self.update_msg['established']

    def update(self, timeout: int = 3600, host: str = 'localhost',
               port: int = 5555, verify: bool = True) -> bool:
        """
        Continuously waits for incoming log info requests or
        server updates from main server, used for both channels;
        log handler and command line handler
        :param host: client hostname (default localhost)
        :param port: connection port number (default 5555)
        :param timeout: duration until timeout (default 1 hour)
        :param verify: should the socket send a verification message (true/false)
        """
        try:
            with s.socket(s.AF_INET, s.SOCK_STREAM) as sock:
                sock.settimeout(timeout)
                sock.connect((host, port))
                if verify:
                    sock.send(bytes(self.update_msg['success'], 'utf-8'))
                with open(f'../transfer/log/log-{DT.now().strftime("%d-%m-%Y")}.txt', 'a+') as file:
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
                            #file.write(f'--LOG[{DT.now().strftime("%H")}]')
                            return False
        except Exception as e:
            self.data.append({'text': str(self.update_msg['failed'])})
            self.DATA.append(self.update_msg['failed'])
            return True


class DataCell(MDLabel):
    """Cellular data in console data"""
    def __init__(self, **kwargs):
        super(DataCell, self).__init__(**kwargs)


class MainApp(MDApp):
    """
    Main Application Window
    - sets app configuration properties
    - initialises all kivy elements onto canvas
    - request a continuous/non-continuous socket attempt
    - sends commands to debug panel to be processed
    - request a clearing of console data
    """

    title = "Terminal Genie"
    icon = './icon/app/app_icon256x256.jpg'
    padding_def = NumericProperty(20)
    status = StringProperty('')
    command = StringProperty('')

    def alt_update(self):
        # restart debugging socket
        thr = threading.Thread(
            target=self.root.ids['debug_panel'].alt_update)
        thr.start()

    def clear_content(self):
        # Tell debug panel to clear data
        self.root.ids['debug_panel'].DATA = ['']

    def send_command(self):
        # Send command to debug panel
        command = self.root.ids['cmd_input'].text
        self.root.ids['debug_panel'].alt_update(command)


if __name__ == '__main__':
    # run app
    MainApp().run()
