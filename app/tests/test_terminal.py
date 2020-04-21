import unittest
from threading import Thread

from app.transfer.server import Server
from app.transfer.terminal import Terminal, log_path, IsolatedSender
import os


s = Server()
t = Terminal(unittest=True)
thr1 = Thread(target=t.two_way_handler, args=(5554,), daemon=True)
thr2 = Thread(target=s.two_way_handler, args=(5555,), daemon=True)
thr1.start()
thr2.start()


class TestTerminal(unittest.TestCase):

    def test_one_way_handler(self):
        """ Test sending bytes over socket to server """

        # test sending a single message
        self.assertTrue(s.one_way_handler(5555, msg='test'))

        # test sending multiple messages
        self.assertTrue(s.one_way_handler(5555, package=['1', '2', '3']))

        # test returning if message empty
        self.assertFalse(s.one_way_handler(5555))

    def test_log_path(self):
        """ Test log path of unity log file/log file directory """

        # test that log_path returns the Editor.log file path
        self.assertEqual(log_path(), f"C:/Users/{os.getlogin()}/AppData/Local/Unity/Editor/Editor.log")

        # test that log_path works with custom log names
        self.assertEqual(log_path('upm.log'), f"C:/Users/{os.getlogin()}/AppData/Local/Unity/Editor/upm.log")

        # test that log_path with 'observer' being true returns the Editor.log directory path
        self.assertEqual(log_path(observer=True), f"C:/Users/{os.getlogin()}/AppData/Local/Unity/Editor/")


if __name__ == '__main__':
    unittest.main()
