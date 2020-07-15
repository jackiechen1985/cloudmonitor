from oslo_config import cfg
from oslo_log import log as logging

from cloudmonitor.conf import ftp
from cloudmonitor.subtasks.subtask_base import SubTaskBase
from cloudmonitor.common.ftp import FtpClient
from cloudmonitor.common.ftp_parser import FtpParser
from cloudmonitor.db.models import SubTaskStatus
from cloudmonitor.influx.models import VlbListenerPm

LOG = logging.getLogger(__name__)

ftp.register_opts()


class VlbListenerPmCollector(SubTaskBase):

    def __init__(self):
        self._context = None

    def save_influx(self, local_file_path_list):
        if self._context:
            for local_file_path in local_file_path_list:
                records = FtpParser.parse_to_list(local_file_path)
                for record in records:
                    db_vlb_listener_pm = VlbListenerPm(
                        CREATE_TIME=record[0],
                        ID=record[1],
                        TRAFFIC_IN=record[2],
                        TRAFFIC_OUT=record[3],
                        REQUESTS_TOTAL=record[4],
                        ACTIVE_CON=record[5],
                        ESTAB_CON=record[6],
                        PACKET_IN=record[7],
                        PACKET_OUT=record[8],
                        ABANDON_CON=record[9],
                        HTTP_QPS=record[10]
                    )
                    self._context.influx_client.write(db_vlb_listener_pm)

    def run(self, context):
        self._context = context
        ftp_client = FtpClient(context, cfg.CONF.ftp.host, cfg.CONF.ftp.port, cfg.CONF.ftp.connection_timeout,
                               cfg.CONF.ftp.username, cfg.CONF.ftp.password)
        ftp_client.connect()
        ftp_client.change_remote_dir(cfg.CONF.ftp.vlb_listener_dir)
        ftp_client.sync_file_to_local_cache()
        local_file_path_list = ftp_client.get_local_file_path_list_by_subtask_id(context.subtask_id)
        if local_file_path_list:
            self.save_influx(local_file_path_list)
            status = SubTaskStatus.SUCCESS.value
        else:
            status = SubTaskStatus.IDLE.value
        return status, None