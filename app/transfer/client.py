# Run as client on local area network
import os
import sys
import argparse
import asyncio
from datetime import datetime as DT
import time
import threading

# List of OPTIONAL command line arguments including...
# --port    port number (integer)
# --time    timeout duration (float)
parser = argparse.ArgumentParser(description="Specify connection parameters")
parser.add_argument('--port', type=int, help="Change port number from default 5555")
parser.add_argument('--time', type=float, help="Sets the duration until the connection times out")
args = parser.parse_args()


class Client():
    timeout: float
    host: str = 'localhost'     # host name
    port: int = 5555            # port number (default is 5555)
    error: str = 'none'

    def __init__(self, auto_connect=False):
        # Asynchronously attempt to connect to terminal
        # and then send verification message. Afterwards,
        # Continue to update terminal until a timeout occurs
        # from inactivity

        # Assign command line arguments to variables if values
        # are given and the values match the correct type
        if args.time and isinstance(args.time, float):
            self.timeout = (args.time*60)
        if args.port and isinstance(args.port, int):
            self.port = args.port

        if auto_connect:
            # Test if connection is available
            asyncio.run(self.connect())

    async def connect(self):
        # Attempt to connect to host otherwise timeout
        # Creates stream reader and writer to receive/send
        # streams to terminal, however, the writer will close
        # once the function ends
        try:
            reader, writer = await \
                asyncio.open_connection(self.host, self.port)
            msg = await reader.read(1024)
            print(msg.decode('utf-8'))
            writer.close()
            await writer.wait_closed()
        except OSError as error:
            # return error if connection timed out and then exit
            self.error = "Timeout Exception Occured:\n%s\n" \
                  "connection timed out, please restart session and check\n" \
                  "that an active wireless connection is available and that\n" \
                  "the server script is running on another machine." % error

    async def update(self):
        # constantly check for updates from terminal
        # every (specified) number of seconds
        reader, writer = await \
            asyncio.open_connection(self.host, self.port)
        msg = await reader.read(1024)

    async def send_msg(self, message: str):
        # Send stream to terminal
        reader, writer = await \
            asyncio.open_connection(self.host, self.port)
        print("You -> %s" % message)
        writer.write(bytes(message, 'utf-8'))
        await writer.drain()


if __name__ == '__main__':
    Client(auto_connect=True)