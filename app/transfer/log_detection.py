import time
import logging
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class LogDetection(FileSystemEventHandler):
    # file/directory handler
    def on_any_event(self, event):
        # if file/directory is created/modified/deleted etc.
        # print info about the event
        print(f'{event.event_type}: {event.src_path}')

if __name__ == "__main__":
    """
    (This script will be for the machine with unity installed)
    
    Continuously checks for file changes to the unity log file
    
    (currently the observer isn't working properly and it's
    checking the current directory for testing purposes)
    """
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')
    path = '.'
    event_handler = LogDetection()
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()

    try:
        # keep observer alive until any keyboard
        # event is triggered (preferably CTRL + c)
        # in terminal
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
