# Run as client on local area network
import socket as s
import argparse

parser = argparse.ArgumentParser(description="Specify connection parameters")
parser.add_argument('--port', type=int, help="Change port number from default 5555")
parser.add_argument('--time', type=float, help="Sets the duration until the connection times out")
args = parser.parse_args()


class Client:
    socket: s.socket                # active socket
    host: str = 'localhost'         # host name
    port: int = 5555                # port number (default is 5555)

    def __init__(self):
        try:
            self.socket = s.socket(s.AF_INET, s.SOCK_STREAM)
            if args.port: self.port = args.port
            if args.time:
                self.socket.settimeout(args.time*60)
        except s.error as error:
            print("could not establish socket: %s" % error)
        finally:
            self.connect()

    def connect(self):
        # Connect to server socket
        self.socket.connect((self.host, self.port))
        message = self.socket.recv(1024)
        print(message.decode('utf-8'))
        self.socket.close()


if __name__ == '__main__':
    Client()