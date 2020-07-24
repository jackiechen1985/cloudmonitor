import json
import logging

from oslo_config import cfg

from rocketmq.client import Producer, Message

from cloudmonitor.conf import rocketmq

LOG = logging.getLogger(__name__)
formatter = logging.Formatter('%(asctime)s %(process)d %(levelname)s %(name)s [-] %(message)s')
file_handler = logging.FileHandler("/var/log/cloudmonitor/rocketmq.log")
file_handler.setFormatter(formatter)
LOG.addHandler(file_handler)

rocketmq.register_opts()


class RocketMqProducer:

    def __init__(self):
        self._producer = Producer(cfg.CONF.rocketmq.producer_group, max_message_size=self.max_message_size)
        self._producer.set_namesrv_addr(cfg.CONF.rocketmq.namesrv_addr)

    @property
    def cm_topic(self):
        return cfg.CONF.rocketmq.cm_topic

    @property
    def pm_topic(self):
        return cfg.CONF.rocketmq.pm_topic

    @property
    def max_message_size(self):
        return cfg.CONF.rocketmq.max_message_size

    def send_sync(self, topic, body, keys=None, tags=None):
        self._producer.start()
        msg = Message(topic)
        msg.set_body(body)
        if keys:
            msg.set_keys(keys)
        if tags:
            msg.set_tags(tags)
        LOG.debug('Send sync message: topic=%s, keys=%s, tags=%s, body_size=%s, body=%s', topic, keys, tags, len(body),
                  json.dumps(json.loads(body), indent=4, separators=(',', ': ')))
        self._producer.send_sync(msg)
        # self._producer.shutdown()
