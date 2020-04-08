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
from kivy.clock import Clock

from app.transfer.command_lookup import CommandLookup

kivy.require('1.11.1')

from kivy.config import Config

Config.set('graphics', 'width', '480')
Config.set('graphics', 'height', '720')
Config.set('graphics', 'minimum_width', '480')
Config.set('graphics', 'minimum_height', '720')
Config.set('graphics', 'resizable', '1')
Config.set('widgets', 'scroll_moves', '10')

from app.transfer.server import Server
from kivymd.app import MDApp
from kivy.uix.recycleview import RecycleView
from kivy.properties import NumericProperty, StringProperty
from kivymd.uix.label import MDLabel
import re
import time
import socket as s
from datetime import datetime as DT
import threading


class DebugPanel(RecycleView, Server, CommandLookup):
    temp_data: [set] = [{'text': 'type ? for a list of commands'}]  # temporary data stored before updating

    def __init__(self, **kwargs):
        super(DebugPanel, self).__init__(**kwargs)  # initialise client super class
        Server.__init__(self, '../transfer/log', 3600, True)  # initialise server
        CommandLookup.__init__(self, '../transfer/log')  # initialise command lookup

        update_thd = threading.Thread(target=self.two_way_handler, args=(5555,))  # monitor for server updates
        watch_data_thd = threading.Thread(target=self.watch_log_update,
                                          daemon=True)  # monitor for data changes until app closes
        update_thd.start()
        watch_data_thd.start()

    def reconnect(self):
        """
        Checks that an update handler is active and lets the user know, or,
        create a new connection to terminal
        """
        if self.test_connection(5554):
            self.data.append({'text': 'connection already established'})
        else:
            update_thd = threading.Thread(target=self.two_way_handler, args=(5555,))
            update_thd.start()

    def watch_log_update(self):
        """
        A thread will run this function in the background every second.
        Compare local data value to client DATA variable. If results are
        different and/or aren't empty, copy to local variable and then
        debug screen should automatically update.
        """
        while True:
            while not self.DATA.empty():
                self.temp_data.append({'text': self.DATA.get_nowait()})
            self.data = self.temp_data
            time.sleep(2)

    def send_command(self, command: str):
        """
        Compare the command against existing commands and then print the
        result to the debug panel
        """
        if self.test_connection(5554):
            self.data = self.lookup(command, self.data)
            self.one_way_handler(5554, command)


class DataCell(MDLabel):
    """Cellular data in debug panel"""
    pass


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

    def reconnect(self):
        self.root.ids['debug_panel'].reconnect()

    def clear_content(self):
        # Tell debug panel to clear data
        self.root.ids['debug_panel'].temp_data = [{'text': 'type ? to see list of commands\n'}]
        self.root.ids['debug_panel'].data = []

    def send_command(self):
        # Send command to debug panel
        command = self.root.ids['cmd_input'].text
        self.root.ids['debug_panel'].send_command(command)


if __name__ == '__main__':
    MainApp().run()
