from oslo_config import cfg
from oslo_log import log as logging
from oslo_concurrency import lockutils

from influxdb_client import InfluxDBClient

from cloudmonitor.conf import influx

LOG = logging.getLogger(__name__)

influx.register_opts()

_synchronized = lockutils.synchronized_with_prefix("cloudmonitor-")
_INFLUX_CLIENT = None


class InfluxClient:

    def __init__(self):
        self._client = InfluxDBClient(url=cfg.CONF.influxdb.url,
                                      token=f'{cfg.CONF.influxdb.username}:{cfg.CONF.influxdb.password}',
                                      org=cfg.CONF.influxdb.organization)

    def _write(self, record):
        write_api = self._client.write_api()
        bucket = f'{cfg.CONF.influxdb.database}/{cfg.CONF.influxdb.retention_policy}'
        write_api.write(bucket=bucket, record=record)
        LOG.debug('InfluxDB write record=%s to bucket=%s', record, bucket)
        write_api.__del__()

    def write(self, model):
        self._write(model.convert_to_point())


@_synchronized("influx-client")
def _create_influx_client():
    global _INFLUX_CLIENT
    if _INFLUX_CLIENT is None:
        _INFLUX_CLIENT = InfluxClient()

    return _INFLUX_CLIENT


def get_influx_client():
    if _INFLUX_CLIENT is None:
        return _create_influx_client()

    return _INFLUX_CLIENT
