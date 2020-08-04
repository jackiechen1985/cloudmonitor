from oslo_config import cfg
from oslo_log import log as logging

from cloudmonitor import conf
from cloudmonitor.db.api import get_writer_session
from cloudmonitor.influx.api import get_influx_client
from cloudmonitor.rocketmq_producer import RocketMqProducer

LOG = logging.getLogger(__name__)

conf.register_opts()


class Context:

    def __init__(self):
        self._session = None
        if cfg.CONF.data_source == 'influxdb':
            self._influx_client = get_influx_client()
        self._rocketmq_producer = None
        self.subtask_id = None

    @property
    def session(self):
        if self._session is None:
            self._session = get_writer_session()
        return self._session

    @property
    def influx_client(self):
        return self._influx_client

    @property
    def rocketmq_producer(self):
        if self._rocketmq_producer is None:
            self._rocketmq_producer = RocketMqProducer()
        return self._rocketmq_producer


def get_context():
    return Context()
