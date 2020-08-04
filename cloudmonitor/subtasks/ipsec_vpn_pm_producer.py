import os
import datetime
import time

from sqlalchemy import and_, or_

from oslo_log import log as logging

from cloudmonitor.conf import ha
from cloudmonitor.subtasks.producer import Producer
from cloudmonitor.subtasks.ipsec_vpn_pm_collector import IpsecVpnPmCollector
from cloudmonitor.common.ftp_parser import FtpParser
from cloudmonitor.influx.models import IpsecVpnPm
from cloudmonitor.db import models

LOG = logging.getLogger(__name__)

ha.register_opts()


class IpsecVpnPmProducer(Producer):

    def run(self):
        with self._context.session.begin(subtransactions=True):
            db_ftp = self._context.session.query(models.Ftp) \
                .join(models.SubTask) \
                .join(models.Task) \
                .filter(and_(models.Task.name == IpsecVpnPmCollector.__name__,
                             or_(models.Ftp.status == models.FtpStatus.DOWNLOAD_SUCCESS.value,
                                 models.Ftp.status == models.FtpStatus.SEND_ERROR.value))).all()

            send_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            timestamp = int(time.mktime(time.strptime(send_time, "%Y-%m-%d %H:%M:%S")))
            instance_list = []
            for ftp in db_ftp:
                db_ftp_producer = models.FtpProducer(time=send_time, subtask_id=self._context.subtask_id, ftp_id=ftp.id)

                if os.path.exists(ftp.local_file_path):
                    db_ftp_producer.data_source = models.FtpProducerDataSource.LOCAL_CACHE.value
                    records = FtpParser.parse_to_list(ftp.local_file_path)
                    for record in records:
                        instance = {
                            'logTime': record[0],
                            'uuid': record[1],
                            'bandwidthInTotal': record[2],
                            'bandwidthOutTotal': record[3],
                            'dataPacketInNumTotal': record[4],
                            'dataPacketOutNumTotal': record[5],
                            'dataSource': record[6]
                        }
                        instance_list.append(instance)
                else:
                    db_ftp_producer.data_source = models.FtpProducerDataSource.INFLUXDB.value
                    records = self._context.influx_client.query(IpsecVpnPm).filter(f'ftp_id == {ftp.id}').all()
                    for record in records:
                        instance = {
                            'logTime': record['logTime'],
                            'uuid': record['uuid'],
                            'bandwidthInTotal': record['bandwidthInTotal'],
                            'bandwidthOutTotal': record['bandwidthOutTotal'],
                            'dataPacketInNumTotal': record['dataPacketInNumTotal'],
                            'dataPacketOutNumTotal': record['dataPacketOutNumTotal'],
                            'dataSource': record['dataSource']
                        }
                        instance_list.append(instance)

                self._context.session.add(db_ftp_producer)

            if not instance_list:
                return models.SubTaskStatus.IDLE.value, None

            try:
                self.send_fragment_msg('IpsecVPN', timestamp, instance_list)
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

            self._context.session.flush()

        return models.SubTaskStatus.SUCCESS.value, None
