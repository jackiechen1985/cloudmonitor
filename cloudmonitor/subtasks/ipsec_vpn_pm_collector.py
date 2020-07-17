from oslo_config import cfg
from oslo_log import log as logging

from cloudmonitor.conf import ftp
from cloudmonitor.subtasks.subtask_base import SubTaskBase
from cloudmonitor.common.ftp import FtpClient
from cloudmonitor.common.ftp_parser import FtpParser
from cloudmonitor.db.models import SubTaskStatus
from cloudmonitor.influx.models import IpsecVpnPm

LOG = logging.getLogger(__name__)

ftp.register_opts()


class IpsecVpnPmCollector(SubTaskBase):

    def __init__(self):
        self._context = None

    def save_influx(self, ftp_list):
        if self._context:
            for ftp in ftp_list:
                records = FtpParser.parse_to_list(ftp.local_file_path)
                for record in records:
                    db_ipsec_vpn_pm = IpsecVpnPm(
                        LogTime=record[0],
                        Uuid=record[1],
                        bandwidthInTotal=record[2],
                        bandwidthOutTotal=record[3],
                        dataPacketInNumTotal=record[4],
                        dataPacketOutNumTotal=record[5],
                        dataSource=record[6],
                        ftp_id=ftp.id
                    )
                    self._context.influx_client.write(db_ipsec_vpn_pm)

    def run(self, context):
        self._context = context
        ftp_client = FtpClient(context, cfg.CONF.ftp.host, cfg.CONF.ftp.port, cfg.CONF.ftp.connection_timeout,
                               cfg.CONF.ftp.username, cfg.CONF.ftp.password)
        ftp_client.connect()
        try:
            ftp_client.change_remote_dir(cfg.CONF.ftp.ipsec_dir)
            ftp_client.sync_file_to_local_cache()
        finally:
            ftp_client.quit()
        ftp_list = ftp_client.get_ftp_list_by_subtask_id(context.subtask_id)
        if ftp_list:
            self.save_influx(ftp_list)
            status = SubTaskStatus.SUCCESS.value
        else:
            status = SubTaskStatus.IDLE.value
        return status, None
