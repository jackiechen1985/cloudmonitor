import os
import datetime
import time
import json

from sqlalchemy import and_, or_

from oslo_config import cfg
from oslo_log import log as logging

from cloudmonitor.conf import ha
from cloudmonitor.subtasks.subtask_base import SubTaskBase
from cloudmonitor.subtasks.vlb_pm_collector import VlbPmCollector
from cloudmonitor.common.ftp_parser import FtpParser
from cloudmonitor.influx.models import VlbPm
from cloudmonitor.common import util
from cloudmonitor.db import models

LOG = logging.getLogger(__name__)

ha.register_opts()


class VlbPmProducer(SubTaskBase):

    def run(self, context):
        with context.session.begin(subtransactions=True):
            db_ftp = context.session.query(models.Ftp) \
                .join(models.SubTask) \
                .join(models.Task) \
                .filter(and_(models.Task.name == VlbPmCollector.__name__,
                        or_(models.Ftp.status == models.FtpStatus.DOWNLOAD_SUCCESS.value,
                            models.Ftp.status == models.FtpStatus.SEND_ERROR.value))).all()

            send_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            timestamp = int(time.mktime(time.strptime(send_time, "%Y-%m-%d %H:%M:%S")))
            instance_list = []
            for ftp in db_ftp:
                db_ftp_producer = models.FtpProducer(time=send_time,
                                                     subtask_id=context.subtask_id, ftp_id=ftp.id)
                context.session.add(db_ftp_producer)

                if os.path.exists(ftp.local_file_path):
                    records = FtpParser.parse_to_list(ftp.local_file_path)
                    for record in records:
                        instance = {
                            'CREATE_TIME': record[0],
                            'ID': record[1],
                            'TRAFFIC_IN': record[2],
                            'TRAFFIC_OUT': record[3],
                            'REQUESTS_TOTAL': record[4]
                        }
                        instance_list.append(instance)
                else:
                    records = context.influx_client.query(VlbPm).filter(f'subtask_id == {ftp.subtask_id}')
                    for record in records:
                        instance = {
                            'CREATE_TIME': record['CREATE_TIME'],
                            'ID': record['ID'],
                            'TRAFFIC_IN': record['TRAFFIC_IN'],
                            'TRAFFIC_OUT': record['TRAFFIC_OUT'],
                            'REQUESTS_TOTAL': record['REQUESTS_TOTAL']
                        }
                        instance_list.append(instance)

            if not instance_list:
                return models.SubTaskStatus.IDLE.value, None

            body = {
                'transId': f'{cfg.CONF.high_availability.host_ip}-{timestamp}-{util.random_string(8)}',
                'type': 'LoadBalancer',
                'timestamp': timestamp,
                'instanceList': instance_list
            }
            try:
                context.rocketmq_producer.send_sync(context.rocketmq_producer.pm_topic, json.dumps(body))
            except Exception as e:
                for ftp in db_ftp:
                    ftp.update({
                        'status': models.FtpStatus.SEND_ERROR.value
                    })
                raise e

            for ftp in db_ftp:
                ftp.update({
                    'status': models.FtpStatus.SEND_SUCCESS.value
                })

            context.session.flush()

        return models.SubTaskStatus.SUCCESS.value, None
