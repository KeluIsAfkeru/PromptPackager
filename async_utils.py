import os
import queue
from tkinter import messagebox
from concurrent.futures import ThreadPoolExecutor

class AsyncEngine:
    def __init__(self, ui_callback_target):
        workers = (os.cpu_count() or 4) * 4
        self.pool = ThreadPoolExecutor(max_workers=workers)
        self.ui_target = ui_callback_target
        self.msg_queue = queue.Queue()
        self._check_queue()

    def _check_queue(self):
        try:
            while True:
                task = self.msg_queue.get_nowait()
                task()
        except queue.Empty:
            pass
        self.ui_target.after(10, self._check_queue)

    def run(self, func, callback, *args):
        def wrapper():
            try:
                res = func(*args)
                self.msg_queue.put(lambda: callback(res))
            except Exception as e:
                err_msg = str(e)
                self.msg_queue.put(lambda: messagebox.showerror("错误", err_msg))
        self.pool.submit(wrapper)