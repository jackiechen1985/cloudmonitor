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
        LOG.info('Unfragment message body: type=%s, timestamp=%s, instanceList length=%d', type, timestamp,
                 len(instance_list))
        fragment_instance_list = list()
        body = {
            'transId': f'{cfg.CONF.high_availability.host_ip}-{timestamp}-{util.random_string(8)}',
            'type': type,
            'timestamp': timestamp,
            'instanceList': fragment_instance_list
        }
        for instance in instance_list:
            if len(json.dumps(body)) > self._context.rocketmq_producer.max_message_size:
                last_instance = fragment_instance_list.pop()
                LOG.info('Fragment message body: transId=%s, type=%s, timestamp=%s, instanceList length=%d',
                         body['transId'], body['type'], body['timestamp'], len(body['instanceList']))
                self._context.rocketmq_producer.send_sync(self._context.rocketmq_producer.pm_topic, json.dumps(body))
                fragment_instance_list.clear()
                fragment_instance_list.append(last_instance)
                body = {
                    'transId': f'{cfg.CONF.high_availability.host_ip}-{timestamp}-{util.random_string(8)}',
                    'type': type,
                    'timestamp': timestamp,
                    'instanceList': fragment_instance_list
                }
            else:
                fragment_instance_list.append(instance)

        if fragment_instance_list:
            LOG.info('Fragment message body: transId=%s, type=%s, timestamp=%s, instanceList length=%d',
                     body['transId'], body['type'], body['timestamp'], len(body['instanceList']))
            self._context.rocketmq_producer.send_sync(self._context.rocketmq_producer.pm_topic, json.dumps(body))
