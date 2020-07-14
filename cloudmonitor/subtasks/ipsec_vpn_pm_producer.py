import datetime
import time
import json

from sqlalchemy import and_, or_

from oslo_config import cfg
from oslo_log import log as logging

from cloudmonitor.conf import ha
from cloudmonitor.subtasks.subtask_base import SubTaskBase
from cloudmonitor.subtasks.ipsec_vpn_pm_collector import IpsecVpnPmCollector
from cloudmonitor.common.ftp_parser import FtpParser
from cloudmonitor.common import util
from cloudmonitor.db import models

LOG = logging.getLogger(__name__)

ha.register_opts()


class IpsecVpnPmProducer(SubTaskBase):

    def run(self, context):
        with context.session.begin(subtransactions=True):
            db_ftp = context.session.query(models.Ftp) \
                .join(models.SubTask) \
                .join(models.Task) \
                .filter(and_(models.Task.name == IpsecVpnPmCollector.__name__,
                        or_(models.Ftp.status == models.FtpStatus.DOWNLOAD_SUCCESS.value,
                            models.Ftp.status == models.FtpStatus.SEND_ERROR.value))).all()

            send_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            timestamp = int(time.mktime(time.strptime(send_time, "%Y-%m-%d %H:%M:%S")))
            instance_list = []
            for ftp in db_ftp:
                db_ftp_producer = models.FtpProducer(time=send_time,
                                                     subtask_id=context.subtask_id, ftp_id=ftp.id)
                context.session.add(db_ftp_producer)
                records = FtpParser.parse_to_list(ftp.local_file_path)
                for record in records:
                    instance = {
                        'LogTime': record[0],
                        'Uuid': record[1],
                        'bandwidthInTotal': record[2],
                        'bandwidthOutTotal': record[3],
                        'dataPacketInNumTotal': record[4],
                        'dataPacketOutNumTotal': record[5],
                        'dataSource': record[6]
                    }
                    instance_list.append(instance)

            if not instance_list:
                raise Warning('No new ftp record found, do nothing!')

            body = {
                'transId': f'{cfg.CONF.high_availability.host_ip}-{timestamp}-{util.random_string(8)}',
                'type': 'IpsecVPN',
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
