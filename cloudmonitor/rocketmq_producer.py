import json

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
    def cm_topic(self):
        return cfg.CONF.rocketmq.cm_topic

    @property
    def pm_topic(self):
        return cfg.CONF.rocketmq.pm_topic

    def send_sync(self, topic, body, keys=None, tags=None):
        self._producer.start()
        msg = Message(topic)
        msg.set_body(body)
        if keys:
            msg.set_keys(keys)
        if tags:
            msg.set_tags(tags)
        LOG.info('%s send sync message: topic=%s, keys=%s, tags=%s, body=%s', RocketMqProducer.__name__, topic, keys,
                 tags, json.dumps(json.loads(body), indent=4, separators=(',', ': ')))
        self._producer.send_sync(msg)
        # self._producer.shutdown()
