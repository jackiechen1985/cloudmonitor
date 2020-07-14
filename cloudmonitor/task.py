from oslo_service import service
from oslo_service import loopingcall


class PeriodicTask(service.ServiceBase):

    def __init__(self, interval, initial_delay, func, *args, **kwargs):
        super(PeriodicTask, self).__init__()

        self._interval = interval
        self._initial_delay = initial_delay
        self.func = func
        self.args = args
        self.kwargs = kwargs
        self._loop = None

    def start(self):
        if self._loop is None:
            self._loop = loopingcall.FixedIntervalLoopingCall(self.func, *self.args, **self.kwargs)
        self._loop.start(interval=self._interval, initial_delay=self._initial_delay)

    def wait(self):
        if self._loop is not None:
            self._loop.wait()

    def stop(self):
        if self._loop is not None:
            self._loop.stop()

    def reset(self):
        self.stop()
        self.wait()
        self.start()
