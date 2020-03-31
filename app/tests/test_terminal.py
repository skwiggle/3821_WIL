from datetime import datetime
from datetime import datetime as DT
import unittest
from app.transfer.terminal_server import Server
from app.transfer.android_client import Client
from app.ui.main import DebugPanel
import os


class MyTestCase(unittest.TestCase):
    client = Client()

    def test_client(self):
        self.assertIsInstance(self.client.DATA[0], str)

    def test_update_msg_success(self):
        self.assertEqual(self.client.update_msg['success'], f'CONSOLE {DT.now().strftime("%I:%M%p")}: {os.getlogin()} is now connected to server' )

    def test_update_msg_failure(self):
        self.assertEqual(self.client.update_msg['failed'], f'CLIENT {DT.now().strftime("%I:%M%p")}: connection failed, check that the server is running')

    def test_update_msg_established(self):
        self.assertEqual(self.client.update_msg['established'], f'CLIENT {DT.now().strftime("%I:%M%p")}: a connection has already been established')

    def test_update_msg_cmd_success(self):
        self.assertEqual(self.client.update_msg['cmd_success'], f'CLIENT {DT.now().strftime("%I:%M%p")}: %s')

    def test_update_msg_cmd_failed(self):
        self.assertEqual(self.client.update_msg['cmd_failed'], f'CLIENT {DT.now().strftime("%I:%M%p")}: command "%s" failed to send')

    def command1_lookup(self):
        client = Client()
        self.assertTrue(client.command_lookup('get log --today'), 'get log --today')
        self.assertEqual(client.command_lookup('get log --tod'), 'no log files exist')


if __name__ == '__main__':
    unittest.main()
