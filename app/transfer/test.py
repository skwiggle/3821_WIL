import threading
import time
import shutil
from threading import Thread


class Timer(Thread):

    def __init__(self, interval):
        Thread.__init__(self)
        self.max_num, self.current_num = interval, interval

    def __call__(self, *args, **kwargs):
        self.start()

    def reset(self):
        self.current_num = self.max_num

    def run(self) -> None:
        while self.current_num != 0:
            print(self.current_num)
            time.sleep(1)
            self.current_num -= 1


t = Timer(3)
t()
time.sleep(2)
t.reset()
t.join()