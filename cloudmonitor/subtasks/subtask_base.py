import abc
import six


@six.add_metaclass(abc.ABCMeta)
class SubTaskBase:

    def __init__(self, context):
        self._context = context

    @abc.abstractmethod
    def run(self):
        raise NotImplementedError()

    def run_supported(self):
        return self.__class__.run != SubTaskBase.run
