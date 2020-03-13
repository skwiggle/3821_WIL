# Run server host on local area network
# Use on computer with unity
import socket as s


socket = s.socket()
host, port = 'localhost', 5555
socket.bind((host, port))

def listen():
    # Listen for client TCP connections and output a clarification
    # message to the client, otherwise, stop listening
    socket.listen(5)
    while True:
       client, address = socket.accept()
       print('Got connection from {} ({})'.format(
           address[0], s.gethostbyaddr(address[0])[0]))
       client.send(bytes('You are now connected to %s' % s.gethostname(), 'utf-8'))
       client.close()


if __name__ == '__main__':
    listen()


