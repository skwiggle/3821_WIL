#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
The main GUI of the application that handles all user
events, connected to the client.
Purposes:
  -    start/close application
  -    display debug log info
  -    receive/send user commands
  -    manually connect to client
  -    read from temporary log files
  -    delete temporary log files
"""

__title__ = 'Terminal Genie'
__version__ = '1.0.0'
__author__ = 'Elliot Charters, Sadeed Ahmad, Max Harvey, Samrat Kunwar, Nguyen Huy Hoang'

import kivy
from kivy.config import Config
from kivymd.app import MDApp
from kivy.core.text import LabelBase
from app.scripts.misc.elements import *
from app.scripts.misc.essentials import format_timestamped_data_text

kivy.require('1.11.1')

# configuration for testing only
# Config.set('graphics', 'width', '480')
# Config.set('graphics', 'height', '720')
# Config.set('graphics', 'minimum_width', '480')
# Config.set('graphics', 'minimum_height', '720')
# Config.set('graphics', 'resizable', '1')
# Config.set('graphics', 'borderless', '0')
Config.set('widgets', 'scroll_moves', '100')

# Add book-antiqua font and load into kivy
# noinspection SpellCheckingInspection
extra_font = [{
    "name": "BookAntiqua",
    "fn_regular": "./ui/font/book-antiqua.ttf",
    "fn_bold": "./ui/font/book-antiqua.ttf",
    "fn_italic": "./ui/font/book-antiqua.ttf",
    "fn_bolditalic": "./ui/font/book-antiqua.ttf"
}]
for font in extra_font:
    LabelBase.register(**font)

class DataCell(MDLabel):
    """ Individual Label UI in :class:`DebugPanel`"""
    pass


# Debugging Panels
DebugPanelFocused()
DebugPanel()
# App Manager
AppManager()
# Screens
MainScreen()
InputFocusedScreen()
# User Oriented Elements
ReconnectBtn()
ClearBtn()
SendBtn()
Input()
Content()


class MainApp(MDApp):
    """
    Main Application Window
    Purpose:
        - sets app configuration properties
        - initialises all kivy elements onto canvas
        - request a continuous/non-continuous socket attempt
        - sends commands to debug panel to be processed
        - request a clearing of console data
    """

    title = "Terminal Genie"
    icon = './ui/icon/app/app_icon256x256.png'
    is_focused: bool = False
    cmd_text: str = ''
    debug_data: [set] = [{}]

    def reconnect(self):
        """ test connection to terminal """
        rec_thd = Thread(target=self.root.get_screen('main').ids['debug_panel'].reconnect)
        rec_thd.start()

    def clear_content(self):
        """ Tell debug panel to clear data """
        self.root.get_screen('main').ids['debug_panel'].data = \
            [format_timestamped_data_text('type ? to see list of commands')]
        self.root.get_screen('main').ids['debug_panel'].temp_data = \
            [format_timestamped_data_text('type ? to see list of commands')]

    def send_command(self):
        """ Send command to debug panel """
        command = self.root.get_screen('main').ids['cmd_input'].text
        cmd_thd = Thread(target=self.root.get_screen('main').ids['debug_panel'].send_command,
                                   args=(command,), name='send_command')
        cmd_thd.start()

    def on_input_focus(self):
        """ switch between screens on text input focus """
        if self.is_focused:
            self.cmd_text = self.root.get_screen('input_focused').ids['cmd_input_focused'].text
            self.root.current = 'main'
            self.is_focused = False
        else:
            self.debug_data = self.root.get_screen('main').ids['debug_panel'].data
            self.root.current = 'input_focused'
            self.root.get_screen('input_focused').ids['debug_panel_focused'].scroll_y = 0
            self.is_focused = True


if __name__ == '__main__':
    MainApp().run()
