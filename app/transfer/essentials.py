"""
Essentials Script

List of functions for smaller purposes used by all scripts that don't
fit anywhere else
"""

import os
from datetime import datetime as dt


def startup():
    """ Make sure the log folder exists, if not, create one"""
    if not os.path.exists('./log'):
        os.mkdir('./log')


def format_debug_text(text: str):
    """
    Convert all text to the recommended size and font

    :param text: The main text having the fotn and size converted
    :type text: str
    """
    return f'[font=BookAntiqua][size=14sp]{text}[/size][/font]'

def timestamp(msg: str):
    """
    A timestamp of the current time with the debug text format applied

    :param msg: the main message
    :type msg: str
    """
    _current_time = dt.now().strftime("%I:%M%p")
    return f'[font=BookAntiqua][size=14sp]{_current_time}: {msg}[/size][/font]'
