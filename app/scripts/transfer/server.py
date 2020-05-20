import asyncio
import os
import re
import socket
from threading import Thread
from datetime import datetime as dt
from queue import Queue
from app.scripts.misc.essentials import local_msg


class Server:
    """
    A server handler in charge or listening and sending information over sockets

    the class consists of one/two way connection handling as well as allowing for
    custom actions upon event change. The server will monitor and communicate events
    from the App front-end back to teh Terminal over a TCP connection
    """

    def __init__(self, temp_log_folder: str = './scripts/transfer/log',
                 timeout: float = 3600, verbose: bool = False):
        self.host = None                            # Ip address of Application (IPv4)
        self.target = None                          # Ip address of Terminal (IPv4)
        self.scroll_down: bool = False              # checks if app should scroll to the bottom
        self.DATA: Queue = Queue()                  # temporary log data storage
        self._temp_log_folder = temp_log_folder     # temporary log directory location
        self.validate_temp_folder()                 # validate the temp log folder exists
        self._timeout = timeout                     # server timeout duration
        self._verbose = verbose                     # checks whether to specify additional error information

    def validate_temp_folder(self) -> None:
        """ Make sure the log folder exists, if not, create one"""
        if not os.path.exists(self._temp_log_folder):
            os.mkdir(self._temp_log_folder)

    async def two_way_handler(self) -> None:
        """Establish and Close Server Connection

        Create an asynchronous server session for the Terminal to
        connect to, hosted on port 5555
        """
        try:
            server = await asyncio.start_server(
                self.handle_requests, self.host, 5555)
            self.DATA.put(f'Server established on {self.host}:5555')
            async with server:
                await server.serve_forever()
        except OSError as error:
            self._append_error(local_msg['server_bind'], error)

    async def handle_requests(self, reader, writer) -> None:
        """Handle TCP Requests

        Handles sending commands back to the Terminal and
        receiving logs or other messages from the Terminal

        :param reader: reader object for receiving incoming byte messages
        :rtype reader: asyncio.StreamReader
        :param writer: writer object for sending byte messages
        :rtype writer: asyncio.StreamWriter
        """

        # continue to read incoming data until --EOF if
        # given and then convert message into decoded list
        # of string values
        data = await reader.readuntil(b'--EOF')
        message = data.decode('utf-8')
        msg_fmt = re.split('\n', message)

        # Display unity log empty error message
        if msg_fmt[-2][:4] == 'tg:>':
            self.DATA.put(local_msg['unity_log_empty']
                          % msg_fmt[-2][4:])

        # Display all unity log files empty error message
        elif msg_fmt == 'tga:>':
            self.DATA.put(local_msg['all_unity_logs_empty'])

        # Any other message is considered a line of a log file
        # The info is written to a local log file within in `./log`
        # folder and then added to the DebugPanel screen to display to the
        # User.
        else:
            # Path to the local log file
            path = f'{self._temp_log_folder}/log-{dt.now().strftime("%d-%m-%Y")}.txt'
            # create a new local log file if none exists
            if not os.path.exists(path):
                with open(path, 'w+'):
                    pass
            with open(path, 'a+') as file:
                for value in msg_fmt:
                    if value != '':
                        file.write(f'{value}\n')
                        self.DATA.put(value)
            # set DebugPanel scroll to the bottom of the app
            # after data is updated to the screen
            self.scroll_down = True
        # Clear buffer and then close connection
        await writer.drain()
        writer.close()

    async def one_way_handler(self, package: [str] = None) -> bool:
        """Sending TCP Messages

        A one-way-handler in charge of sending messages to the Terminal in
        the form of string lists where the last element is always '--EOF'
        to inform the Terminal server of when to stop listening.

        :param package: data to send to Terminal
        """
        try:
            # open connection to
            reader, writer = await asyncio.open_connection(
                self.host, 5554)

            if package:
                message = [f"{x}\n".encode('utf-8') for x in package]
                writer.writelines(message)
                writer.write(b'--EOF')
                await writer.drain()
                writer.close()
                return True
        except Exception as error:
            print(error)
            return False

    def _append_error(self, error: str, verbose_msg) -> None:
        """Append error to Screen

        Appends error to application debug panel to display to the user.

        :param error: custom error message
        :param verbose_msg: system error message, only appends if
                            `_verbose` is True
        :type verbose_msg: any exception error type
        """
        self.DATA.put(error)
        if self._verbose:
            self.DATA.put(f"---> {verbose_msg}")

    # noinspection PyBroadException,PyUnboundLocalVariable
    def test_connection(self, port: int) -> bool:
        """
        Test the connection to terminal
        :param port: outbound port number
        """
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(2)
                sock.connect((self.target, port))
                sock.send(b'tc:>')
                self._append_error(local_msg['connection_established'], f"Connected to "
                                   f"{self.target} on ports {port} and {port + 1}")
        except socket.timeout:
            sock.close()
            return False


if __name__ == '__main__':
    """ Unit testing only """
    s = Server('./log')
    t1 = Thread(target=asyncio.run, args=(s.two_way_handler(),))
    t1.start()
