import json
import socket
import pickle

data = json.dumps({k: v for k, v in enumerate(range(10, 2))})

host, port = 'localhost', 5555

socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
socket.connect((host, port))
client, address = socket.accept()
client.sendall(data)
print("sent")
client.close()
