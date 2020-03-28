# The main GUI of the application that handles all user
# events, connected to the client.
# Purposes:
#  -    start/close application
#  -    display debug log info
#  -    receive/send user commands
#  -    manually connect to client
#  -    read from temporary log files

import kivy
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
from kivy.properties import NumericProperty, StringProperty, ListProperty
from kivymd.label import MDLabel
from kivy.clock import Clock
import re
from datetime import datetime as DT
import time
import asyncio
import threading

class mainApp(MDApp):
    title = "What should we call the program"
    icon = './icon/app/app_icon1024x1024.jpg'
    padding_def = NumericProperty(20)
    status = StringProperty('')
    command = StringProperty('')

    def on_start(self):
        self.setup()

    def send_command(self):
        command = self.root.ids['cmd_input'].text
        self.client.send_cmd(command)

    def setup(self):
        try:
            client = Client(auto_connect=False)
            self.status = client.get_connection
            log_msg = MDLabel(
                text=self.status,
                theme_text_color = 'Custom',
                text_color = (1, 1, 1, 1)
            )
            Clock.schedule_once(lambda x: self.root.ids['content_layout']
                                .add_widget(log_msg))
        except:
            self.status = 'a problem occured,\nplease reload the app'


if __name__ == '__main__':
    mainApp().run()
