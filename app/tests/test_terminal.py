from datetime import datetime
import unittest
from app.transfer.terminal_server import Server
from app.transfer.android_client import Client


class MyTestCase(unittest.TestCase):

    def test_client(self):
        client = Client()
        self.assertIsInstance(client.DATA[0], str)

if __name__ == '__main__':
    unittest.main()
