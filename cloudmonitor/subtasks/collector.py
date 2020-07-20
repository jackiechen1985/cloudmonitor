import abc
import six

from oslo_log import log as logging

from cloudmonitor.subtasks.subtask_base import SubTaskBase

LOG = logging.getLogger(__name__)


@six.add_metaclass(abc.ABCMeta)
class Collector(SubTaskBase):

    @abc.abstractmethod
    def save_influx(self, ftp_list):
        raise NotImplementedError()
