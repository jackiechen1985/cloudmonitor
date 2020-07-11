from oslo_config import cfg
from oslo_log import log as logging

from rocketmq.client import Producer, Message

from cloudmonitor.conf import rocketmq

LOG = logging.getLogger(__name__)

rocketmq.register_opts()


class RocketMqProducer:

    def __init__(self):
        self._producer = Producer(cfg.CONF.rocketmq.producer_group)
        self._producer.set_namesrv_addr(cfg.CONF.rocketmq.namesrv_addr)

    @property
    def configure_topic(self):
        return cfg.CONF.rocketmq.configure_topic

    @property
    def performance_topic(self):
        return cfg.CONF.rocketmq.performance_topic

    def send_sync(self, topic, keys, tags, body):
        self._producer.start()
        msg = Message(topic)
        msg.set_keys(keys)
        msg.set_tags(tags)
        msg.set_body(body)
        LOG.info('%s sending message: topic=%s, keys=%s, tags=%s, body=%s', RocketMqProducer.__name__, topic, keys,
                 tags, body)
        self._producer.send_sync(msg)
        self._producer.shutdown()
