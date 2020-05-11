# -*- coding: utf-8 -*-
# The main GUI of the application that handles all user
# events, connected to the client.
# Purposes:
#  -    start/close application
#  -    display debug log info
#  -    receive/send user commands
#  -    manually connect to client
#  -    read from temporary log files
#  -    delete temporary log files

__title__ = 'Terminal Genie'
__version__ = '1.0.0'
__author__ = 'Elliot Charters, Sadeed Ahmad, Max Harvey, Samrat Kunwar, Nguyen Huy Hoang'

import kivy
from kivy.config import Config
import time
import threading
from kivymd.app import MDApp
from kivy.uix.image import Image
from kivy.uix.widget import Widget
from kivymd.uix.label import MDLabel
from kivy.core.text import LabelBase
from app.transfer.server import Server
from kivy.uix.textinput import TextInput
from kivy.uix.recycleview import RecycleView
from kivy.uix.button import ButtonBehavior, Button
from app.transfer.command_lookup import CommandLookup
from app.transfer.essentials import format_timestamped_data_text
from kivy.uix.screenmanager import Screen, ScreenManager, NoTransition

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

# classes representing UI elements that need to be displayed
# in main.py in order to work
class DebugPanelFocused(RecycleView): pass


class DebugPanel(RecycleView, Server, CommandLookup):
    # temporary data stored before updating
    temp_data = [format_timestamped_data_text('type ? for a list of commands')]

    def __init__(self, **kwargs):
        # initialise super classes
        super(DebugPanel, self).__init__(**kwargs)  # initialise client super class
        Server.__init__(self, './transfer/log', 3600, True)  # initialise server
        CommandLookup.__init__(self, './transfer/log')  # initialise command lookup

        # setup threads
        update_thd = threading.Thread(target=self.two_way_handler, args=(5555,),
                                      daemon=True)  # monitor for server updates
        watch_data_thd = threading.Thread(target=self.watch_log_update,
                                          daemon=True)  # monitor for data changes until app closes
        update_thd.start()
        watch_data_thd.start()

    def reconnect(self):
        """
        Checks that an update handler is active and lets the user know, or,
        create a new connection to terminal
        """
        if not self.test_connection(5554):
            update_thd = threading.Thread(target=self.two_way_handler, args=(5555,))
            update_thd.start()
        self.scroll_y = 0

    def watch_log_update(self):
        """
        A thread will run this function in the background every second.
        Compare local data value to client DATA variable. If results are
        different and/or aren't empty, copy to local variable and then
        debug screen should automatically update.
        """
        while True:
            if not self.DATA.empty():
                # Retrieve incoming data from server script and display to the log
                while not self.DATA.empty():
                    self.temp_data.append(format_timestamped_data_text(self.DATA.get(block=True)))
                self.data = self.temp_data
                # Set screen scroll to bottom once data is updated to screen
                if self.scroll_down:
                    self.scroll_y = 0
                    self.scroll_down = False
            # wait 1 second before updating again
            time.sleep(1)

    def send_command(self, command: str):
        """
        Compare the command against existing commands and then print the
        result to the :class:`DebugPanel`

        :param command: The command sent from the user input
        :type command: str
        """
        # Check validity of command
        self.temp_data = self.lookup(command, self.data)
        # Send command
        self.one_way_handler(5554, f'kc:>{command}' if self.check(command) else f'uc:>{command}')
        # Set scroll to bottom
        self.scroll_y = 0


class AppManager(ScreenManager):
    def __init__(self, **kwargs):
        super(AppManager, self).__init__(**kwargs)
        self.transition = NoTransition()


class MainScreen(Screen): pass


class InputFocusedScreen(Screen):
    def on_enter(self, *args):
        text_input = self.children[0].children[1].children[0].children[0]
        text_input.focus = True
        if text_input.text == 'Enter command...':
            text_input.text = ''


class ReconnectBtn(ButtonBehavior, Image): pass
class ClearBtn(Button): pass
class SendBtn(Button): pass
class Input(Widget): pass
class DataCell(MDLabel): pass


class Content(TextInput):
    def __init__(self, **kwargs):
        super(Content, self).__init__(**kwargs)
        self.text = 'Enter command...'


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
        rec_thd = threading.Thread(target=self.root.get_screen('main').ids['debug_panel'].reconnect)
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
        cmd_thd = threading.Thread(target=self.root.get_screen('main').ids['debug_panel'].send_command,
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
