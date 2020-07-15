from oslo_config import cfg
from oslo_log import log as logging

from cloudmonitor.conf import ftp
from cloudmonitor.subtasks.subtask_base import SubTaskBase
from cloudmonitor.common.ftp import FtpClient
from cloudmonitor.common.ftp_parser import FtpParser
from cloudmonitor.db.models import SubTaskStatus
from cloudmonitor.influx.models import NatPm

LOG = logging.getLogger(__name__)

ftp.register_opts()


class NatPmCollector(SubTaskBase):

    def __init__(self):
        self._context = None

    def save_influx(self, local_file_path_list):
        if self._context:
            for local_file_path in local_file_path_list:
                records = FtpParser.parse_to_list(local_file_path)
                for record in records:
                    db_nat_pm = NatPm(
                        LogTime=record[0],
                        Uuid=record[1],
                        connectNum=record[2],
                        dataPacketInNum=record[3],
                        dataPacketOutNum=record[4],
                        bandwidthIn=record[5],
                        bandwidthOut=record[6],
                        dataSource=record[7]
                    )
                    self._context.influx_client.write(db_nat_pm)

    def run(self, context):
        self._context = context
        ftp_client = FtpClient(context, cfg.CONF.ftp.host, cfg.CONF.ftp.port, cfg.CONF.ftp.connection_timeout,
                               cfg.CONF.ftp.username, cfg.CONF.ftp.password)
        ftp_client.connect()
        ftp_client.change_remote_dir(cfg.CONF.ftp.nat_dir)
        ftp_client.sync_file_to_local_cache()
        local_file_path_list = ftp_client.get_local_file_path_list_by_subtask_id(context.subtask_id)
        if local_file_path_list:
            self.save_influx(local_file_path_list)
            status = SubTaskStatus.SUCCESS.value
        else:
            status = SubTaskStatus.IDLE.value
        return status, None
