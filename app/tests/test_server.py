import unittest
from app.transfer.server import Server
from terminal.other_platforms.terminal import Terminal
from threading import Thread


class TestServer(unittest.TestCase):

    s = Server()
    t = Terminal(unittest=True)
    thr1 = Thread(target=t.two_way_handler, args=(5554,), daemon=True)
    thr2 = Thread(target=s.two_way_handler, args=(5555,), daemon=True)
    thr1.start()
    thr2.start()

    def test_one_way_handler(self):
        """ Test sending bytes over socket to terminal """

        # test sending a single message
        self.assertTrue(self.s.one_way_handler(5554, msg='test'))

        # test sending multiple messages
        self.assertTrue(self.s.one_way_handler(5554, package=['1', '2', '3']))

        # test returning if message empty
        self.assertFalse(self.s.one_way_handler(5554))

    def test_test_connection(self):
        """ Test testing if a connection is available """

        # test connection active
        self.assertTrue(self.s.test_connection(5554))

        # test connection inactive
        self.assertFalse(self.s.test_connection(5556))


if __name__ == '__main__':
    unittest.main()
