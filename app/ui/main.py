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
import asyncio
import threading


class DebugPanel(RecycleView):
    def __init__(self, **kwargs):
        super(DebugPanel, self).__init__(**kwargs)
        self.data = []

    def append(self, element: str):
        self.data.append({'text': str(element)})


class DataCell(MDLabel):
    def __init__(self, **kwargs):
        super(DataCell, self).__init__(**kwargs)


class MainApp(MDApp):
    title = "What should we call the program"
    icon = './icon/app/app_icon1024x1024.jpg'
    padding_def = NumericProperty(20)
    status = StringProperty('')
    command = StringProperty('')

    def on_start(self):
        self.setup()

    def setup(self):
        try:
            self.status = Client(False).get_connection
            Clock.schedule_once(self.root.ids['debug_panel'].append(self.status))
        except Exception as e:
            self.status = f'a problem occurred, please reload the app\n-> {e}'

    def clear_content(self):
        self.root.ids['debug_panel'].data = []

    def send_command(self):
        command = self.root.ids['cmd_input'].text
        client = Client(ignore_setup=True, command=command)


if __name__ == '__main__':
    MainApp().run()
