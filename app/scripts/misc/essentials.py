"""
*****************
Essentials Script
*****************

List of functions for smaller purposes used by all scripts that don't
fit anywhere else
"""

from datetime import datetime as dt

def fmt_datacell(text: str) -> object:
    """Format Data into RecycleView DataCell Object

    Reformat text into a DataCell object to be used by kivy in order
    to display the info to the screen. Also formats the text to the
    book-antiqua font at size 14p

    :param text: The main text having the font and size converted
    :returns: a dictionary containing the reformatted text
    """
    _current_time = dt.now().strftime("%I:%M%p")
    return {'text': f'[font=BookAntiqua][size=14sp]{_current_time}: {text}[/size][/font]'}


# List of re-occurring error messages, easily referencable
local_msg: dict = {
    'target_server': 'Server attempting to start on current port: \'%s\'',
    'server_established': 'established server',
    'server_bind': 'The host or target IP specified cannot be reached',
    'server_connect_failed': 'failed to connect to the server',
    'connection_established': 'connection established',
    'connection_closed': 'failed to send message because no connection was found%s',
    'timeout': 'connection timed out',
    'unity_log_empty': 'Log file %s is empty',
    'all_unity_logs_empty': 'No new updates from unity',
    'unknown': 'unknown error, please restart terminal'
}
