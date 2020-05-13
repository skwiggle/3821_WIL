#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Essentials Script

List of functions for smaller purposes used by all scripts that don't
fit anywhere else
"""

from datetime import datetime as dt

def fmt_datacell(text: str):
    """
    Extends :method:`format_data_text` to also include a timestamp

    :param text: The main text having the font and size converted
    :returns: a dictionary containing the reformatted text
    :rtype: dict[str, str]
    """
    _current_time = dt.now().strftime("%I:%M%p")
    return {'text': f'[font=BookAntiqua][size=14sp]{_current_time}: {text}[/size][/font]'}


# List of re-occurring error messages, easily referencable
local_msg: dict = {
    'server_established': 'established server',
    'server_connect_failed': 'failed to connect to the server',
    'connection_established': 'connection established',
    'connection_closed': 'failed to send message because no connection was found',
    'timeout': 'connection timed out',
    'stream_active': 'please wait until previous message has sent',
    'unity_log_empty': 'log file %s is empty',
    'all_unity_logs_empty': 'no new updates from unity',
    'unknown': 'unknown error, please restart terminal'
}
