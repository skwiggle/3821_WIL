# Run from remote terminal on a local area network and connects
# to android application. Must be run on a machine with Unity
# installed.
# purposes:
# -   Handles connection updates from any client
# -   reads log file and sends data to application
# -   receives messages from application
# -   sends messages to application

import os
import sys
import socket as s
import argparse
import time
from datetime import datetime as DT
import multiprocessing

""" List of OPTIONAL command line arguments including...
    --port    port number (integer)
    --time    timeout duration (float) """
parser = argparse.ArgumentParser(description="Specify connection parameters")
parser.add_argument('--port', type=int, help="Change port number from default 5555")
parser.add_argument('--time', type=float, help="Sets the duration until the connection times out")
args = parser.parse_args()


class Server:
    socket: s.socket         # active socket
    host: str = 'localhost'  # host name
    port: int = 5555         # port number (default is 5555)

    def __init__(self):
        try:
            # create socket for IPV4 connections
            self.socket = s.socket(s.AF_INET, s.SOCK_STREAM)
            # Assign command line arguments to variables if values
            # are given and the values match the correct type
            if args.port:
                self.port = args.port
            if args.time:
                self.socket.settimeout(args.time*60)
        except s.error as error:
            print("could not establish socket: %s" % error)
        finally:
            self.socket.bind((self.host, self.port))
            self.listen()
            # listen for connection infinitely
            # every 5 seconds
            while True:
                self.listen()
                time.sleep(5)

    def listen(self) -> None:
        """
        Listen for client TCP connections and output a verification
        message to the client, otherwise, stop listening for
        incoming requests
        """
        self.socket.listen(5)
        while True:
            current_time = DT.now().strftime("%I:%M%p")
            try:
                client, address = self.socket.accept()      # get current client object and address of receiver
                msg = "[%s]\tSuccessfully connected to %s (%s)" % \
                      (current_time, address[0],
                       s.gethostbyaddr(address[0])[0])      # create verification message
                client.send(bytes(msg, 'utf-8'))            # send verification message
                rec = client.recv(1024)                     # receives decoded verification message from
                print(rec.decode('utf-8'))                                  # application and prints
            except s.timeout as error:
                print("%s\tconnection timed out: %s" % (current_time, error))
            finally:
                client.close()      # closes client and flushes buffer


class ReadLogFile:
    """
    Reads each line of the unity log file depending on the platform.
    """
    location: str = None
    loglocations: dict = {
        'windows': 'C:/Users/%s/AppData/Local/Unity/Editor/Editor.log' %
                   (os.getlogin()),
        'macos': '~/Library/Logs/Unity/Editor.log',
        'linux': '~/.config/unity3d/Editor.log'
    }

    def __init__(self):
        self.check_location_exists()

    def check_location_exists(self) -> str:
        '''
        Check the debug log file location for each platform
        :return: URL string or raise error (none)
        '''
        platform: str = sys.platform
        # sets location specific to platform
        # either windows, mac os or linux/unix
        for pf in self.loglocations.keys():
            if platform.__contains__('win'):
                platform = pf
                break
            if platform.__contains__('mac'):
                platform = pf
                break
            if platform.__contains__('lin'):
                platform = pf
                break
        # assigns global location to local loction
        # if it exists
        if os.path.exists(self.loglocations[platform]):
            self.location = self.loglocations[platform]
        else:
            # raise error
            print("File could not be found at \'%s\';\n" %
            self.loglocations[platform])
            raise FileExistsError

    def read_lines(self, url: str) -> iter([bytes]):
        """
        Reads log file and returns all lines of text as
        and array of bytes with a timestamp at the beginning
        of each line
        :param url: location of log file
        :return: an iterator to iterate over each line of text
        """
        current_time = DT.now().strftime("%I:%m%p")     # get current time
        with open(url, 'r') as file:                    # open file
            return iter([bytes("[%s]: %s" % (current_time, line),
                               'utf-8') for line in file])

    def read_until_eof(self, line):
        # print each line
        # testing purpose only
        print(line)


if __name__ == '__main__':
    server = Server()         # start server
    reader = ReadLogFile()      # read log file
    def read_log():
        """
        Split reading the log file between more than 1 cpu core
        allowing it to be read faster
        """
        lines = reader.read_lines(reader.location)
        pool = multiprocessing.Pool(int(multiprocessing.cpu_count()/2))
        pool.map(reader.read_until_eof, lines)
        pool.close()
        pool.join()







