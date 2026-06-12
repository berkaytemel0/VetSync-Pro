from PyQt6.QtCore import QThread, pyqtSignal

_active_workers = []


class Worker(QThread):
    result = pyqtSignal(object)
    error  = pyqtSignal(str)

    def __init__(self, fn, *args, **kwargs):
        super().__init__()
        self._fn     = fn
        self._args   = args
        self._kwargs = kwargs
        _active_workers.append(self)
        self.finished.connect(lambda: _active_workers.remove(self)
                              if self in _active_workers else None)

    def run(self):
        try:
            self.result.emit(self._fn(*self._args, **self._kwargs))
        except Exception as e:
            self.error.emit(str(e))