# Run server host on local area network
# Use on computer with unity
import socket as s
import argparse
from datetime import datetime

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

    def listen(self):
        # Listen for client TCP connections and output a clarification
        # message to the client, otherwise, stop listening
        self.socket.listen(5)
        while True:
           current_time = datetime.now().strftime("%I:%M%p")
           client, address = self.socket.accept()
           print('%s\tConnected to %s (%s)' % (current_time,
                address[0], s.gethostbyaddr(address[0])[0]))
           client.send(bytes('%s\tSuccessfully connected to %s (%s)' %
                (current_time, address[0], s.gethostbyaddr(address[0])[0]), 'utf-8'))
           client.close()


if __name__ == '__main__':
    Server()


