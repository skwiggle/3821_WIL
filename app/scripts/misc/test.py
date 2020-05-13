import socket

s = socket.socket()
host = '192.168.0.19'
port = 9077
s.connect((host, port))
print(s.recv(1024))