# Run server host on local area network
# Use on computer with unity
import socket as s
import argparse

parser = argparse.ArgumentParser(description="Specify connection parameters")
parser.add_argument('--port', help="Change port number from default 5555")
args = parser.parse_args()

class Server:
    socket: s.socket  # active socket
    host: str = 'localhost'  # host name
    port: int = 5555  # port number (default is 5555)

    def __init__(self, timeout_mins: float):
        try:
            self.socket = s.socket(s.AF_INET, s.SOCK_STREAM)
            if args.port:
                self.port = args.port
        except s.error as error:
            print("could not establish socket: %s" % error)
        finally:
            self.socket.bind((self.host, self.port))
            self.socket.settimeout(timeout_mins*60)



    def listen(self):
        # Listen for client TCP connections and output a clarification
        # message to the client, otherwise, stop listening
        self.socket.listen(5)
        while True:
           client, address = self.socket.accept()
           print('Got connection from {} ({})'.format(
               address[0], s.gethostbyaddr(address[0])[0]))
           client.send(bytes('You are now connected to %s' % s.gethostname(), 'utf-8'))
           client.close()


if __name__ == '__main__':
    Server(1)


