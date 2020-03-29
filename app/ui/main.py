# The main GUI of the application that handles all user
# events, connected to the client.
# Purposes:
#  -    start/close application
#  -    display debug log info
#  -    receive/send user commands
#  -    manually connect to client
#  -    read from temporary log files

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
        self.data = [{'text': str(i)*40} for i in range(100)]

class DataCell(MDLabel):
    def __init__(self, **kwargs):
        super(DataCell, self).__init__(**kwargs)

class MainApp(MDApp):
    title = "What should we call the program"
    icon = './icon/app/app_icon1024x1024.jpg'
    padding_def = NumericProperty(20)
    status = StringProperty('')
    command = StringProperty('')
    data = []

    def on_start(self):
        self.setup()

    def send_command(self):
        command = self.root.ids['cmd_input'].text
        self.client.send_cmd(command)

    def setup(self):
        try:
            client = Client(auto_connect=False)
            self.status = client.get_connection
            # at the moment I've disabled this because I recently reworked
            # the debug panel to use a recycleview meaning this no longer
            # works but I'll try to fix it today
            '''
            log_msg = MDLabel(
                text=self.status,
                theme_text_color='Custom',
                text_color=(1, 1, 1, 1)
            )
            clear_btn = MDRaisedButton(
                height=50,
                text='clear',
                pos_hint={'right': 1},
                md_bg_color=(0.2, 0.6, 1, 1),
                specific_text_color=[1, 1, 1, 0.87]
            )
            Clock.schedule_once(lambda x: self.root.ids['content_layout']
                                .add_widget(log_msg))
            Clock.schedule_once(lambda x: self.root.ids['bottom_panel']
                                .add_widget(clear_btn))'''
        except:
            self.status = 'a problem occured,\nplease reload the app'


if __name__ == '__main__':
    MainApp().run()
