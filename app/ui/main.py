from kivy.uix.widget import Widget

from app.transfer.android_client import Client

import kivy

kivy.require('1.11.1')
from kivy.config import Config
Config.set('graphics', 'width', '640')
Config.set('graphics', 'height', '960')
Config.set('graphics', 'minimum_width', '360')
Config.set('graphics', 'minimum_height', '480')
Config.set('graphics', 'resizable', '1')
Config.set('widgets', 'scroll_moves', '10')

from kivy.graphics import Color, Rectangle
from kivymd.app import MDApp
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.app import App
from kivy.lang import Builder
from kivy.properties import NumericProperty, StringProperty, ListProperty
from kivymd.button import MDRaisedButton
from kivymd.label import MDLabel
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivymd.textfields import MDTextField
from kivy.uix.scrollview import ScrollView
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.core.window import Window
from kivymd.spinner import MDSpinner
from kivy.clock import Clock

import time
from datetime import datetime as DT
import asyncio

padding_def = 20


class Manager(ScreenManager):
    status = StringProperty('loading')
    def __init__(self, **kwargs):
        super(Manager, self).__init__(**kwargs)

    def setup(self):
        try:
            client = Client(auto_connect=False)
            self.status = client.update()
            if not self.status.__contains__('connection failed'):
                self.current = 'main'
        except:
            self.status = 'a problem occured,\nplease reload the app'


class Content(GridLayout):
    def __init__(self, **kwargs):
        GridLayout.__init__(self, **kwargs)
        self.print_to_screen(
            [str(f'[{x}] This is a line of text')
             for x in range(50)])

    def print_to_screen(self, lines: [str]):
        for line in lines:
            self.add_widget(MDLabel(
                text=line
            ))


class DebugPanel(BoxLayout): pass


class CmdPanel(BoxLayout):
    client_num = NumericProperty(1)
    pass


class mainApp(MDApp):

    title = "What should we call the program"
    icon = './icon/placeholder.jpg'
    padding_def = NumericProperty(20)
    global_error = StringProperty('none')
    status: ListProperty = ['', '']


if __name__ == '__main__':
    mainApp().run()
