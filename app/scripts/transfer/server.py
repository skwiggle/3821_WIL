import asyncio
import os
import re
import time
import socket
from threading import Thread
from datetime import datetime as dt
from queue import Queue
from app.scripts.misc.essentials import local_msg, public_msg


# noinspection PyArgumentList,PyBroadException
class Server:
    """
    A server handler in charge or listening and sending information over sockets

    the class consists of one/two way connection handling as well as allowing for
    custom actions upon event change.
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
        """
        Constantly listen for incoming messages from other hosts.

        Should be used to handle incoming log updates from the terminal
        or incoming commands from the application. Also displays error info.
        """
        try:
            server = await asyncio.start_server(
                self.handle_requests, self.host, 5555)
            self.DATA.put(local_msg['server_established'])
            async with server:
                await server.serve_forever()
        except OSError as error:
            self._append_error(public_msg['server_bind'], error)

    async def handle_requests(self, reader, writer):
        """
        Constantly listen for incoming messages from other hosts.
        Should be used to handle incoming log updates from the terminal
        or incoming commands from the application. Also displays error info.
        """

        data = await reader.readuntil(b'--EOF')
        message = data.decode('utf-8')
        msg_fmt = re.split('\n', message)

        if msg_fmt[-2][:4] == 'tg:>':
            self.DATA.put(local_msg['unity_log_empty']
                          % msg_fmt[-2][4:])

        elif msg_fmt == 'tga:>':
            self.DATA.put(local_msg['all_unity_logs_empty'])

        else:
            path = f'{self._temp_log_folder}/log-{dt.now().strftime("%d-%m-%Y")}.txt'
            if not os.path.exists(path):
                with open(path, 'w+'):
                    pass
            with open(path, 'a+') as file:
                for value in msg_fmt:
                    if value != '':
                        file.write(f'{value}\n')
                        self.DATA.put(value)
            self.scroll_down = True

        await writer.drain()
        writer.close()

    async def one_way_handler(self, package: [str] = None) -> bool:
        """
        """
        reader, writer = await asyncio.open_connection(
            self.host, 5554)

        message: list = []
        if package:
            message = [f"{x}\n".encode('utf-8') for x in package]
            writer.writelines(message)
            writer.write(b'--EOF')
            await writer.drain()
            writer.close()
            return True

        return False

    def _append_error(self, error: str, verbose_msg) -> None:
        """
        Appends error to application debug panel to display to the user.

        :param error: custom error message
        :param verbose_msg: system error message, only appends if
                            `_verbose` is True
        :type verbose_msg: any exception error type
        """
        self.DATA.put(error)
        if self._verbose:
            self.DATA.put(f"---> {verbose_msg}")

    # noinspection PyBroadException
    def test_connection(self, port: int) -> bool:
        """
        Test the connection to terminal

        :param port: outbound port number
        """
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            sock.connect((self.target, port))
            sock.send(b'tc:>')
            self._append_error(local_msg['connection_established'], f"Connected to "
                                                                    f"{self.target} on ports {port} and {port + 1}")
            sock.close()
            return True
        except socket.timeout:
            sock.close()
            return False


if __name__ == '__main__':
    """ Unit testing only """
    s = Server('./log')
    t1 = Thread(target=asyncio.run, args=(s.two_way_handler(),))
    t1.start()
