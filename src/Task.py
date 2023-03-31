import time
from PyQt5 import QtCore, QtWidgets


class Task (QtCore.QObject):

    updated = QtCore.pyqtSignal(bool, bool, bool, int)

    def __init__(self, processor_thread):

        super(Task, self).__init__()

        self.processor_thread = processor_thread
        self.kill_thread = False

    def video_processing_task(self):

        completed = 0

        self.updated.emit(False, True, False, completed)

        while self.processor_thread.is_alive():

            if self.kill_thread:

                self.processor_thread.stop()
                break

            self.updated.emit(False, True, False, int(completed))
            time.sleep(0.10)

            if completed < 99:
                completed += 0.009

        self.updated.emit(True, False, True, 100)
