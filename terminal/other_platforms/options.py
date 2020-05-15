import json
from socket import socket

options = {
    "ipv4": "0.0.0.0",
    "timeout": 3600,
    "verbose": True
}

with open('test.json', 'w') as file:
    json.dump(options, file)

with open('test.json', 'r') as file:
    new_data = json.load(file)
    print(new_data)