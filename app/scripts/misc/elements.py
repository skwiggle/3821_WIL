#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re
import time
from threading import Thread

from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.recycleview import RecycleView
from kivy.uix.screenmanager import ScreenManager, NoTransition, Screen
from kivy.uix.textinput import TextInput
from kivy.uix.widget import Widget
from kivymd.uix.textfield import MDTextField

from app.scripts.misc.essentials import fmt_datacell
from app.scripts.transfer.command_lookup import CommandLookup
from app.scripts.transfer.server import Server


class DebugPanelFocused(RecycleView):
    """
    version of :class:`DebugPanel` for
    :class:`InputFocusedScreen`
    """
    pass

class AppManager(ScreenManager):
    """ Main Screen Manager """
    def __init__(self, **kwargs):
        super(AppManager, self).__init__(**kwargs)
        self.transition = NoTransition()

# Screens
class StartScreen(Screen):
    """
    The Startup Screen used to validate the IPv4 address to the
    target host machine
    """
    pass


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
class IPInput(MDTextField):
    def __init__(self, **kwargs):
        super(IPInput, self).__init__(**kwargs)
        self.text = self.get_saved_ipv4()

    def get_saved_ipv4(self):
        ip_address = ''
        with open('./settings_config.txt', 'r') as file:
            option_ipv4 = re.split('=', file.readline())
            if option_ipv4[0] == 'ipv4' and option_ipv4[1] != '':
                ip_address = option_ipv4[1]
        return ip_address

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