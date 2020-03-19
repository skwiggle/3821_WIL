# Run server host on local area network
# Use on computer with unity
# Handles all connection updates
import os
import sys
import socket as s
import argparse
from datetime import datetime as DT
import time
import multiprocessing
import asyncio

# adds arguments when running script from the console
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
            self.socket = s.socket(s.AF_INET, s.SOCK_STREAM)
            if args.port: self.port = args.port
            if args.time:
                self.socket.settimeout(args.time*60)
        except s.error as error:
            print("could not establish socket: %s" % error)
        finally:
            self.socket.bind((self.host, self.port))
            self.listen()
            '''
            while True:
                self.listen()
                time.sleep(5)'''

    def listen(self) -> None:
        # Listen for client TCP connections and output a clarification
        # message to the client, otherwise, stop listening
        self.socket.listen(5)
        while True:
            current_time = DT.now().strftime("%I:%M%p")
            try:
                client, address = self.socket.accept()
                msg = "[%s]\tSuccessfully connected to %s (%s)" % \
                      (current_time, address[0], s.gethostbyaddr(address[0])[0])
                print(msg)
                client.send(bytes(msg, 'utf-8'))
                rec = client.recv(1024).decode('utf-8')
                print(rec)
            except s.timeout as error:
                print("%s\tconnection timed out: %s" % (current_time, error))
            finally:
                client.close()


class ReadLogFile:
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
        :return: URL string
        '''
        platform: str = sys.platform
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
        if os.path.exists(self.loglocations[platform]):
            self.location = self.loglocations[platform]
        else:
            print("File could not be found at \'%s\';\n" %
            self.loglocations[platform])
            raise FileExistsError

    def read_lines(self, url: str) -> iter([bytes]):
        current_time = DT.now().strftime("%I:%m%p")
        with open(url, 'r') as file:
            return iter([bytes("[%s]: %s" % (current_time, line),
                               'utf-8') for line in file])

    def read_until_eof(self, line):
        print(line)


if __name__ == '__main__':
    # server = Server()
    reader = ReadLogFile()
    def read_log():
        lines = reader.read_lines(reader.location)
        pool = multiprocessing.Pool(int(multiprocessing.cpu_count()/2))
        pool.map(reader.read_until_eof, lines)
        pool.close()
        pool.join()
    read_log()






