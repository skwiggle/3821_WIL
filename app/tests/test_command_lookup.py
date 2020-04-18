import unittest
from datetime import datetime as dt
from app.transfer.command_lookup import CommandLookup
import os


class TestCommandLookup(unittest.TestCase):
    """ Test the command lookup class """
    cmd_lo = CommandLookup('../transfer/log')

    def test_lookup(self):
        """
        Test that commands are reformatted correctly to avoid failure
        """
        _timestamp = dt.now().strftime("%I:%M%p")

        # test that a plain command works
        self.assertEqual(self.cmd_lo.lookup('get log', []), [])

        # test that all characters except numbers and letters are removed
        self.assertEqual(self.cmd_lo.lookup('gET   LoG', []), [])

        # test that non-letter/number characters except '?' work
        self.assertEqual(self.cmd_lo.lookup('?', []),
                         [{'text': line} for line in self.cmd_lo.command_list])

    def test_get_log(self):
        """
        Test that command lookup retrieves log info with/without parameters
        """
        _timestamp = dt.now().strftime("%I:%M%p")

        # test that it returns the blank file message and creates file
        self.assertEqual(self.cmd_lo.lookup('get log --today', []),
                         [{'text': f'{_timestamp}: no previous logs from today, blank file created'}])

        # test that it returns an end of file message now that it has been created
        self.assertEqual(self.cmd_lo.lookup('get log --today', []),
                         [{'text': f'{_timestamp}: end of file----\n'}])

        # test retrieval with specific dates and creates file
        self.assertEqual(self.cmd_lo.lookup('get log --01-01-2020', []),
                         [{'text': f'{_timestamp}: no previous logs from that day, blank file created'}])

        # test retrieval with specific dates after file creation
        self.assertEqual(self.cmd_lo.lookup('get log --01-01-2020', []),
                         [{'text': f'{_timestamp}: end of file----\n'}])

        # test that '-' and '/' optionally both work
        self.assertEqual(self.cmd_lo.lookup('get log --01/01/2020', []),
                         [{'text': f'{_timestamp}: end of file----\n'}])

class TestCommandLookupClear(unittest.TestCase):
    """
    Test the command lookup classes clear_log function

    This function had to be run seperately due to the nature of unit testing
    running asynchronously which means the files themselves cannot be deleted
    while the stream is still open in another process.
    """
    cmd_lo = CommandLookup('../transfer/log')

    def test_clear_log(self):
        """
        Test that command lookup retrieves clear messages and deletes files correctly
        """
        _timestamp = dt.now().strftime("%I:%M%p")

        # test that it returns the log file deleted message and deletes file
        self.assertEqual(self.cmd_lo.lookup('clear log --today', []),
            [{'text': f'{_timestamp}: log file at ../transfer/log/log-{dt.now().strftime("%d-%m-%Y")}.txt deleted'}])

        # test that it returns the no log file found message after file deletion
        self.assertEqual(self.cmd_lo.lookup('clear log --today', []),
            [{'text': f'{_timestamp}: no log file found at ../transfer/log/log-{dt.now().strftime("%d-%m-%Y")}.txt'}])

        # test file deletion with specific date
        self.assertEqual(self.cmd_lo.lookup('clear log --01-01-2020', []),
            [{'text': f'{_timestamp}: log file at ../transfer/log/log-01-01-2020.txt deleted'}])

        # test file deletion with specific date after file deletion
        self.assertEqual(self.cmd_lo.lookup('clear log --01-01-2020', []),
            [{'text': f'{_timestamp}: no log file found at ../transfer/log/log-01-01-2020.txt'}])

        # test file deletion with specific date using '/' instead of '-' in date string
        with open('../transfer/log/log-01-01-2020.txt', 'w+'): pass
        self.assertEqual(self.cmd_lo.lookup('clear log --01/01/2020', []),
            [{'text': f'{_timestamp}: log file at ../transfer/log/log-01-01-2020.txt deleted'}])

        # test the deletion of all log files
        self.assertEqual(self.cmd_lo.lookup('clear logs', []), [{'text': f'{_timestamp}: all log files deleted'}])


if __name__ == '__main__':
    unittest.main()
