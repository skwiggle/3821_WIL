import watchdog
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer
import time

class EventHandler(FileSystemEventHandler):
    def on_any_event(self, event):
        print(f'something happened')

obs = Observer()
eventhandling = EventHandler()
obs.schedule(eventhandling, '.', recursive=True)
obs.start()
try:
    while True:
        time.sleep(1)
except:
    obs.stop()
obs.join()
