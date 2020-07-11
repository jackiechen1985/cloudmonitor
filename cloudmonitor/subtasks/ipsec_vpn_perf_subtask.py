from oslo_config import cfg
from oslo_log import log as logging

from cloudmonitor.conf import ftp
from cloudmonitor.subtasks.subtask_base import SubTaskBase
from cloudmonitor.ftp import FtpClient
from cloudmonitor.influx.models import IpsecVpnPerformance

LOG = logging.getLogger(__name__)

ftp.register_opts()


class IpsecVpnPerfSubTask(SubTaskBase):

    def __init__(self):
        self._context = None

    def save_influx(self, local_file_path_list):
        for file in local_file_path_list:
            with open(file, 'r') as fp:
                while True:
                    line = fp.readline()
                    if not line:
                        break
                    fields = line.split(';')
                    db_ipsec_vpn_performance = IpsecVpnPerformance(
                        LogTime=fields[0],
                        Uuid=fields[1],
                        bandwidthInTotal=fields[2],
                        bandwidthOutTotal=fields[3],
                        dataPacketInNumTotal=fields[4],
                        dataPacketOutNumTotal=fields[5],
                        dataSource=fields[6]
                    )
                    if self._context:
                        self._context.influx_client.write(db_ipsec_vpn_performance)

    def run(self, context):
        self._context = context
        ftp_client = FtpClient(context, cfg.CONF.ftp.host, cfg.CONF.ftp.port, cfg.CONF.ftp.connection_timeout,
                               cfg.CONF.ftp.username, cfg.CONF.ftp.password)
        ftp_client.connect()
        ftp_client.change_remote_dir(cfg.CONF.ftp.ipsec_dir)
        ftp_client.sync_file_to_local_cache()
        local_file_path_list = ftp_client.get_local_file_path_list_by_subtask_id(context.subtask_id)
        self.save_influx(local_file_path_list)
