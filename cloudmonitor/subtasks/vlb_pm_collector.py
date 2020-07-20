from oslo_config import cfg
from oslo_log import log as logging

from cloudmonitor.conf import ftp
from cloudmonitor.subtasks.collector import Collector
from cloudmonitor.common.ftp import FtpClient
from cloudmonitor.common.ftp_parser import FtpParser
from cloudmonitor.db.models import SubTaskStatus
from cloudmonitor.influx.models import VlbPm

LOG = logging.getLogger(__name__)

ftp.register_opts()


class VlbPmCollector(Collector):

    def save_influx(self, ftp_list):
        if self._context:
            for ftp in ftp_list:
                records = FtpParser.parse_to_list(ftp.local_file_path)
                for record in records:
                    db_vlb_pm = VlbPm(
                        CREATE_TIME=record[0],
                        ID=record[1],
                        TRAFFIC_IN=record[2],
                        TRAFFIC_OUT=record[3],
                        REQUESTS_TOTAL=record[4],
                        ftp_id=ftp.id
                    )
                    self._context.influx_client.write(db_vlb_pm)

    def run(self):
        ftp_client = FtpClient(self._context, cfg.CONF.ftp.host, cfg.CONF.ftp.port, cfg.CONF.ftp.connection_timeout,
                               cfg.CONF.ftp.username, cfg.CONF.ftp.password)
        ftp_client.connect()
        try:
            ftp_client.change_remote_dir(cfg.CONF.ftp.vlb_dir)
            ftp_client.sync_file_to_local_cache()
        finally:
            ftp_client.quit()
        ftp_list = ftp_client.get_ftp_list_by_subtask_id(self._context.subtask_id)
        if ftp_list:
            self.save_influx(ftp_list)
            status = SubTaskStatus.SUCCESS.value
        else:
            status = SubTaskStatus.IDLE.value
        return status, None
