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
from kivymd.button import MDRaisedButton
from kivymd.label import MDLabel
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.core.window import Window
from functools import partial
import asyncio

padding_def = 20


class MainLayout(GridLayout):
    debug_panel: BoxLayout
    cmd_panel: BoxLayout

    def __init__(self):
        GridLayout.__init__(self)

        self.cols = 1
        self.padding = padding_def
        self.spacing = padding_def / 2

        self.debug_panel = DebugPanel()
        self.cmd_panel = CmdPanel()

        self.active_connection()
        self.add_widget(self.debug_panel)
        self.add_widget(self.cmd_panel)

    def active_connection(self):
        client = Client(auto_connect=False)
        self.debug_panel.add_widget(MDLabel(
            text=client.update()))


class DebugPanel(BoxLayout):
    layout: GridLayout

    def __init__(self, **kwargs):
        BoxLayout.__init__(self, **kwargs)
        self.size = (Window.width, Window.height * 0.6)
        layout = GridLayout(
            cols=1, size_hint=(None, None),
            width=self.width, height=self.height
        )
        layout.bind(minimum_height=layout.setter('height'))
        # 50 rows of scrollable placeholder text
        layout.add_widget(MDLabel(text=f"50 rows of text\n" * 25, size=self.size,
                       size_hint=(None, None)))
        layout.add_widget(MDLabel(text=f"50 rows of text\n" * 25, size=self.size,
                                  size_hint=(None, None)))

        root = ScrollView(size_hint=(None, None), size=self.size,
                          do_scroll_x=False)
        root.add_widget(layout)
        self.add_widget(root)


class CmdPanel(BoxLayout):
    def __init__(self, **kwargs):
        BoxLayout.__init__(self, **kwargs)
        self.orientation = 'vertical'
        self.size_hint = (1, 0.4)
        self.spacing = 10

        cmd_input = TextInput(
            size_hint_y=None,
            height=self.height,
            font_size=(Window.height / 42)
        )

        def send_cmd(instance):
            client = Client(auto_connect=True)
            client.send_cmd(cmd_input.text)

        send_btn = MDRaisedButton(
            text='send',
            md_bg_color=(0.2, 0.6, 1, 1),
            specific_text_color=[1, 1, 1, 0.87],
            pos_hint={'right': 1},
            on_press=send_cmd
        )

        self.add_widget(cmd_input)
        self.add_widget(send_btn)


class MainApp(MDApp):
    title = "What should we call the program"
    icon = './icon/placeholder.jpg'

    def build(self):
        return MainLayout()


if __name__ == '__main__':
    MainApp().run()
