'''
This class was be run concurrently with the
other scripts to detect whenever the unity file
is modified and then will cause the remote terminal
to send a log update request

(watchdog not working for some reason)
'''

import time


import watchdog
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer


class FileEvents(FileSystemEventHandler):
    def on_modified(self, event):
        print(f'{event.src_path}\n')


logObsv = Observer()
logObsv.schedule(FileEvents, './log/',
                 recursive=True)

logObsv.start()
try:
    while True:
        time.sleep(1)
except:
    logObsv.stop()
    logObsv.join()
