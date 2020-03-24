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
from kivy.app import App
from kivy.lang import Builder
from kivy.properties import NumericProperty, StringProperty, OptionProperty
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
from kivymd.tabs import MDTabbedPanel, MDTab

from datetime import datetime as DT
import asyncio

padding_def = 20


class MainLayout(GridLayout): pass


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
    padding_def = NumericProperty(20)
    title = "What should we call the program"
    icon = './icon/placeholder.jpg'
    pass


if __name__ == '__main__':
    mainApp().run()
