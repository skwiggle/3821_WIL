#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import time
from threading import Thread

from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.recycleview import RecycleView
from kivy.uix.screenmanager import ScreenManager, NoTransition, Screen
from kivy.uix.textinput import TextInput
from kivy.uix.widget import Widget
from kivymd.uix.label import MDLabel

from app.scripts.misc.essentials import format_timestamped_data_text
from app.scripts.transfer.command_lookup import CommandLookup
from app.scripts.transfer.server import Server


class DebugPanelFocused(RecycleView):
    """
    version of :class:`DebugPanel` for
    :class:`InputFocusedScreen`
    """
    pass

class DebugPanel(RecycleView, Server, CommandLookup):
    """
    Debug Panel in charge of displaying and managing updates on
    information to the screen. Extends :class:`Server` for connectivity
    and :class:`CommandLookup` for command validity check.
    """
    # temporary data stored before updating
    temp_data = [format_timestamped_data_text('type ? for a list of commands')]

    def __init__(self, **kwargs):
        # initialise super classes
        super(DebugPanel, self).__init__(**kwargs)  # initialise client super class
        Server.__init__(self, './transfer/log', 3600, True)  # initialise server
        CommandLookup.__init__(self, './transfer/log')  # initialise command lookup

        # setup threads
        update_thd = Thread(target=self.two_way_handler, args=(5555,), daemon=True)  # monitor for server updates
        watch_data_thd = Thread(target=self.watch_log_update, daemon=True)  # monitor for data changes until app closes
        update_thd.start()
        watch_data_thd.start()

    def reconnect(self):
        """
        Checks that an update handler is active and lets the user know, or,
        create a new connection to terminal
        """
        if not self.test_connection(5554):
            update_thd = Thread(target=self.two_way_handler, args=(5555,))
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
        """
        # Check validity of command
        self.temp_data = self.lookup(command, self.data)
        # Send command
        self.one_way_handler(5554, f'kc:>{command}' if self.check(command) else f'uc:>{command}')
        # Set scroll to bottom
        self.scroll_y = 0

class AppManager(ScreenManager):
    """ Main Screen Manager """
    def __init__(self, **kwargs):
        super(AppManager, self).__init__(**kwargs)
        self.transition = NoTransition()

# Screens
class MainScreen(Screen):
    """
    Main screen for when the user is doing anything else
    except inputting text
    """
    pass

class InputFocusedScreen(Screen):
    """ Screen for when user needs to input text """
    def on_enter(self, *args):
        text_input = self.children[0].children[1].children[0].children[0]
        text_input.focus = True
        if text_input.text == 'Enter command...':
            text_input.text = ''

# User Oriented Elements
class ReconnectBtn(ButtonBehavior, Image):
    """ Reconnect button UI"""
    pass

class ClearBtn(Button):
    """ Clear button UI """
    pass

class SendBtn(Button):
    """ Send button UI """
    pass

class Input(Widget):
    """ :class:`Content` Container UI"""
    pass

class Content(TextInput):
    """ User input field UI"""
    def __init__(self, **kwargs):
        super(Content, self).__init__(**kwargs)
        self.text = 'Enter command...'