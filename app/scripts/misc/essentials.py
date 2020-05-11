#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Essentials Script

List of functions for smaller purposes used by all scripts that don't
fit anywhere else
"""

from datetime import datetime as dt


def format_normal_text(text: str):
    """
    Convert all text to the recommended size and font

    :param text: The main text having the font and size converted
    :returns: Text with the BookAntiqua font, size 14sp
    :rtype: str
    """
    return f'[font=BookAntiqua][size=14sp]{text}[/size][/font]'

def format_data_text(text: str):
    """
    Formats message into a dictionary set as the value of 'text',
    also appending the properties of :method:`format_debug_text`

    :param text: The main text having the font and size converted
    :returns: a dictionary containing the reformatted text
    :rtype: dict[str, str]
    """
    return {'text': f'[font=BookAntiqua][size=14sp]{text}[/size][/font]'}

def timestamp(msg: str):
    """
    A timestamp of the current time with the debug text format applied

    :param msg: the main message
    :returns: a timestamped version of the reformatted text
    :rtype: dict[str, str]
    """
    _current_time = dt.now().strftime("%I:%M%p")
    return f'[font=BookAntiqua][size=14sp]{_current_time}: {msg}[/size][/font]'

def format_timestamped_data_text(text: str):
    """
    Extends :method:`format_data_text` to also include a timestamp

    :param text: The main text having the font and size converted
    :returns: a dictionary containing the reformatted text
    :rtype: dict[str, str]
    """
    _current_time = dt.now().strftime("%I:%M%p")
    return {'text': f'[font=BookAntiqua][size=14sp]{_current_time}: {text}[/size][/font]'}