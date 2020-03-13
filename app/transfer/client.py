# Run as client on local area network
import socket as s


class Client:
    socket: s.socket                # active socket
    host: str = 'localhost'         # host name
    port: int = 5555                # port number (default is 5555)

    def __init__(self):
        try:
            self.socket = s.socket(s.AF_INET, s.SOCK_STREAM)
        except s.error as error:
            print("could not establish socket: %s" % error)
        finally:
            self.connect()

    def changePort(self, new_port: int):
        # change port number
        self.port = new_port

    def connect(self):
        # Connect to server socket
        self.socket.connect((self.host, self.port))
        message = self.socket.recv(1024)
        print(message.decode('utf-8'))
        self.socket.close()


if __name__ == '__main__':
    Client()