import abc
import six
import json

from oslo_config import cfg
from oslo_log import log as logging

from cloudmonitor.subtasks.subtask_base import SubTaskBase
from cloudmonitor.common import util

LOG = logging.getLogger(__name__)


@six.add_metaclass(abc.ABCMeta)
class Producer(SubTaskBase):

    def send_fragment_msg(self, type, timestamp, instance_list):
        body = {
            'transId': f'{cfg.CONF.high_availability.host_ip}-{timestamp}-{util.random_string(8)}',
            'type': type,
            'timestamp': timestamp,
            'instanceList': instance_list
        }
        body_data = json.dumps(body)
        if len(json.dumps(body)) < self._context.rocketmq_producer.max_message_size:
            LOG.info('Fragment message body: transId=%s, type=%s, timestamp=%s, len(instanceList)=%d',
                     body['transId'], body['type'], body['timestamp'], len(body['instanceList']))
            self._context.rocketmq_producer.send_sync(self._context.rocketmq_producer.pm_topic, body_data)
        else:
            delimiter = int(len(instance_list) / 2)
            self.send_fragment_msg(type, timestamp, instance_list[:delimiter])
            self.send_fragment_msg(type, timestamp, instance_list[delimiter:])
