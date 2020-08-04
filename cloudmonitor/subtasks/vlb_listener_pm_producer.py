import os
import datetime
import time

from sqlalchemy import and_, or_

from oslo_config import cfg
from oslo_log import log as logging

from cloudmonitor import conf
from cloudmonitor.conf import ha
from cloudmonitor.subtasks.producer import Producer
from cloudmonitor.subtasks.vlb_listener_pm_collector import VlbListenerPmCollector
from cloudmonitor.common.ftp_parser import FtpParser
from cloudmonitor.influx.models import VlbListenerPm
from cloudmonitor.db import models

LOG = logging.getLogger(__name__)

conf.register_opts()
ha.register_opts()


class VlbListenerPmProducer(Producer):

    def run(self):
        with self._context.session.begin(subtransactions=True):
            db_ftp = self._context.session.query(models.Ftp) \
                .join(models.SubTask) \
                .join(models.Task) \
                .filter(and_(models.Task.name == VlbListenerPmCollector.__name__,
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
                            'createTime': record[0],
                            'uuid': record[1],
                            'trafficIn': record[2],
                            'trafficOut': record[3],
                            'requestsTotal': record[4],
                            'activeCon': record[5],
                            'estabCon': record[6],
                            'packetIn': record[7],
                            'packetOut': record[8],
                            'abandonCon': record[9],
                            'httpQps': record[10]
                        }
                        instance_list.append(instance)
                elif cfg.CONF.data_source == 'influxdb':
                    db_ftp_producer.data_source = models.FtpProducerDataSource.INFLUXDB.value
                    records = self._context.influx_client.query(VlbListenerPm).filter(f'ftp_id == {ftp.id}').all()
                    for record in records:
                        instance = {
                            'createTime': record['createTime'],
                            'uuid': record['uuid'],
                            'trafficIn': record['trafficIn'],
                            'trafficOut': record['trafficOut'],
                            'requestsTotal': record['requestsTotal'],
                            'activeCon': record['activeCon'],
                            'estabCon': record['estabCon'],
                            'packetIn': record['packetIn'],
                            'packetOut': record['packetOut'],
                            'abandonCon': record['abandonCon'],
                            'httpQps': record['httpQps']
                        }
                        instance_list.append(instance)

                self._context.session.add(db_ftp_producer)

            if not instance_list:
                return models.SubTaskStatus.IDLE.value, None

            try:
                self.send_fragment_msg('LbListener', timestamp, instance_list)
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
