import unittest
from datetime import datetime as dt
from app.scripts.transfer.command_lookup import CommandLookup


class TestCommandLookup(unittest.TestCase):
    """ Test the command lookup class """
    cmd_lo = CommandLookup('../scripts/transfer/log')

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
                         [{'text': '[font=BookAntiqua][size=14sp][/size][/font]'},
                          {'text': '[font=BookAntiqua][size=14sp]?: get list of commands[/size][/font]'},
                          {'text': '[font=BookAntiqua][size=14sp]get log: request current '
                                   'log from unity[/size][/font]'},
                          {'text': '[font=BookAntiqua][size=14sp]get log --today: get all '
                                   'logs from today[/size][/font]'},
                          {'text': '[font=BookAntiqua][size=14sp]get log --00-01-2000: get '
                                   'all logs from specific day on day-month-year[/size][/font]'},
                          {'text': '[font=BookAntiqua][size=14sp]clear logs: delete all temporary logs[/size][/font]'},
                          {'text': '[font=BookAntiqua][size=14sp]clear log --today: clear '
                                   'all logs from today[/size][/font]'},
                          {'text': '[font=BookAntiqua][size=14sp]clear log --00-01-2000: clear '
                                   'log of specific day[/size][/font]'},
                          {'text': '[font=BookAntiqua][size=14sp][/size][/font]'}])

    def test_get_log(self):
        """
        Test that command lookup retrieves log info with/without parameters
        """
        _timestamp = dt.now().strftime("%I:%M%p")

        # test that it returns the blank file message and creates file
        self.assertEqual(self.cmd_lo.lookup('get log --today', []),
                         [{'text': f'[font=BookAntiqua][size=14sp]{_timestamp}: '
                                   f'no previous logs from today, blank file created[/size][/font]'}])

        # test that it returns an end of file message now that it has been created
        self.assertEqual(self.cmd_lo.lookup('get log --today', []),
                         [{'text': f'[font=BookAntiqua][size=14sp]{_timestamp}: end of file----[/size][/font]'}])

        # test retrieval with specific dates and creates file
        self.assertEqual(self.cmd_lo.lookup('get log --01-01-2020', []),
                         [{'text': f'[font=BookAntiqua][size=14sp]{_timestamp}: '
                                   f'no previous logs from that day, blank file created[/size][/font]'}])

        # test retrieval with specific dates after file creation
        self.assertEqual(self.cmd_lo.lookup('get log --01-01-2020', []),
                         [{'text': f'[font=BookAntiqua][size=14sp]{_timestamp}: end of file----[/size][/font]'}])

        # test that '-' and '/' optionally both work
        self.assertEqual(self.cmd_lo.lookup('get log --01/01/2020', []),
                         [{'text': f'[font=BookAntiqua][size=14sp]{_timestamp}: end of file----[/size][/font]'}])

class TestCommandLookupClear(unittest.TestCase):
    """
    Test the command lookup classes clear_log function
    This function had to be run seperately due to the nature of unit testing
    running asynchronously which means the files themselves cannot be deleted
    while the stream is still open in another process.
    """
    cmd_lo = CommandLookup('../scripts/transfer/log')

    def test_clear_log(self):
        """
        Test that command lookup retrieves clear messages and deletes files correctly
        """
        _timestamp = dt.now().strftime("%I:%M%p")

        # test that it returns the log file deleted message and deletes file
        self.assertEqual(self.cmd_lo.lookup('clear log --today', []),
            [{'text': f'[font=BookAntiqua][size=14sp]{_timestamp}: '
                      f'log file at ../scripts/transfer/log/log-{dt.now().strftime("%d-%m-%Y")}'
                      f'.txt deleted[/size][/font]'}])

        # test that it returns the no log file found message after file deletion
        self.assertEqual(self.cmd_lo.lookup('clear log --today', []),
            [{'text': f'[font=BookAntiqua][size=14sp]{_timestamp}: '
                      f'no log file found at ../scripts/transfer/log/log-{dt.now().strftime("%d-%m-%Y")}'
                      f'.txt[/size][/font]'}])

        # test file deletion with specific date
        self.assertEqual(self.cmd_lo.lookup('clear log --01-01-2020', []),
            [{'text': f'[font=BookAntiqua][size=14sp]{_timestamp}: '
                      f'log file at ../scripts/transfer/log/log-01-01-2020.txt deleted[/size][/font]'}])

        # test file deletion with specific date after file deletion
        self.assertEqual(self.cmd_lo.lookup('clear log --01-01-2020', []),
            [{'text': f'[font=BookAntiqua][size=14sp]{_timestamp}: '
                      f'no log file found at ../scripts/transfer/log/log-01-01-2020.txt[/size][/font]'}])

        # test file deletion with specific date using '/' instead of '-' in date string
        with open('../scripts/transfer/log/log-01-01-2020.txt', 'w+'): pass
        self.assertEqual(self.cmd_lo.lookup('clear log --01/01/2020', []),
            [{'text': f'[font=BookAntiqua][size=14sp]{_timestamp}: '
                      f'log file at ../scripts/transfer/log/log-01-01-2020.txt deleted[/size][/font]'}])

        # test the deletion of all log files
        self.assertEqual(self.cmd_lo.lookup('clear logs', []),
                         [{'text': f'[font=BookAntiqua][size=14sp]{_timestamp}: '
                                   f'all log files deleted[/size][/font]'}])


if __name__ == '__main__':
    unittest.main()
