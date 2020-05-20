#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
**************
Terminal Genie
**************

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
kivy.require('1.11.1')

# configuration for testing only
from kivy.config import Config

# Default configuration options for non-android
# devices (Testing)
Config.set('graphics', 'minimum_width', '480')
Config.set('graphics', 'minimum_height', '720')
Config.set('graphics', 'width', '480')
Config.set('graphics', 'height', '720')
Config.set('graphics', 'resizable', '1')
Config.set('graphics', 'borderless', '0')
Config.set('widgets', 'scroll_moves', '100')

from kivymd.app import MDApp
from kivy.core.text import LabelBase
from app.scripts.misc.elements import *
from app.scripts.misc.essentials import fmt_datacell
from app.scripts.misc.settings_config import _ipv4_is_valid
import re

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

    title = "Terminal Genie"    # Application title
    icon = './ui/icon/app/app_icon256x256.png'  # Application icon
    is_focused: bool = False    # boolean, is the input focused on
    cmd_text: str = ''      # Input field text value
    debug_data: [set] = [{}]    # temporary data storage location to transfer data between pages

    def reconnect(self) -> None:
        """ Test connection to terminal """
        rec_thd = Thread(target=self.root.get_screen('main').ids['debug_panel'].reconnect)
        rec_thd.start()

    def refresh_host(self) -> None:
        """ Reset host field to null """
        self.root.get_screen('start').ids['host_ip'].text = ''

    def refresh_target(self):
        """ Reset target field to null """
        self.root.get_screen('start').ids['target_ip'].text = ''

    def clear_content(self) -> None:
        """ Tell debug panel to clear data """
        self.root.get_screen('main').ids['debug_panel'].data = \
            [fmt_datacell('type ? to see list of commands')]
        self.root.get_screen('main').ids['debug_panel'].temp_data = \
            [fmt_datacell('type ? to see list of commands')]

    def send_command(self):
        """ Send command to DebugPanel """
        command = self.root.get_screen('main').ids['cmd_input'].text
        cmd_thd = Thread(target=self.root.get_screen('main').ids['debug_panel'].send_command,
                         args=(command,), name='send_command')
        cmd_thd.start()

    def on_input_focus(self) -> None:
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

    def start_screen_submit(self) -> None:
        """
        Save host and target IPs to settings and then change
        start screen to main screen
        """
        host_ipv4 = self.root.get_screen('start').ids['host_ip'].text
        target_ipv4 = self.root.get_screen('start').ids['target_ip'].text
        if _ipv4_is_valid(host_ipv4) and _ipv4_is_valid(target_ipv4):
            self.root.get_screen('start').ids['host_ip'].set_host()
            self.root.get_screen('start').ids['target_ip'].set_target()
            self.root.get_screen('main').ids['debug_panel'].start_server()
            self.root.current = 'main'


if __name__ == '__main__':
    MainApp().run()
