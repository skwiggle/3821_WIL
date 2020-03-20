# Run from application on local area network and connect to remote terminal
# will automatically timeout after [--time] minutes
# purposes:
# -   requests log file text from remote terminal
# -   receives messages from terminal
# -   sends messages back to terminal

import argparse
import asyncio

""" List of OPTIONAL command line arguments including...
    --port    port number (integer)
    --time    timeout duration (float) """
parser = argparse.ArgumentParser(description="Specify connection parameters")
parser.add_argument('--port', type=int, help="Change port number from default 5555")
parser.add_argument('--time', type=float, help="Sets the duration until the connection times out")
args = parser.parse_args()


class Client():
    timeout: float              # time until connection resets
    host: str = 'localhost'     # host name
    port: int = 5555            # port number (default is 5555)
    error: str = 'none'         # global error string

    def __init__(self, auto_connect=False):
        """
        Asynchronously attempt to connect to terminal
        and then send verification message. Afterwards,
        Continue to update terminal until a timeout occurs
        from inactivity
        :param auto_connect: Attempt a connection to terminal
                             upon being initialised
        """
        # Assign command line arguments to variables if values
        # are given and the values match the correct type
        if args.time and isinstance(args.time, float):
            self.timeout = (args.time*60)
        if args.port and isinstance(args.port, int):
            self.port = args.port
        # Test if connection is available
        if auto_connect:
            asyncio.run(self.connect())

    async def connect(self) -> None:
        """
        Connect to host otherwise timeout
        """
        try:
            """ reader and writer are stream readers/writers that will
                automatically read incoming messages or send messages
                until closed """
            reader, writer = await \
                asyncio.open_connection(self.host, self.port)       # open connection or continue if connection fails
            msg = await reader.read(1024)                           # receive message
            print(msg.decode('utf-8'))                              # decode bytes to string value and print
            writer.close()                                          # closes stream writer and flushes buffer
            await writer.wait_closed()                              # waits until writer is closed before finishing
        except OSError as error:
            # return operating system error if connection timed out
            self.error = "Timeout Exception Occured:\n%s\n" \
                  "connection timed out, please restart session and check\n" \
                  "that an active wireless connection is available and that\n" \
                  "the server script is running on another machine." % error

    async def send_msg(self, message: str) -> None:
        """
        Open a connection and send an encoded message
        """
        reader, writer = await \
            asyncio.open_connection(self.host, self.port)
        print("You -> %s" % message)
        writer.write(bytes(message, 'utf-8'))
        await writer.drain()


if __name__ == '__main__':
    Client(auto_connect=True)