from oslo_config import cfg
from oslo_log import log as logging
from oslo_concurrency import lockutils

from influxdb_client import InfluxDBClient
from influxdb_client.client.write_api import SYNCHRONOUS

from cloudmonitor.conf import influx

LOG = logging.getLogger(__name__)

influx.register_opts()

_synchronized = lockutils.synchronized_with_prefix("cloudmonitor-")
_INFLUX_CLIENT = None


class QueryObject:
    def __init__(self, obj_list):
        self._obj_list = obj_list

    def first(self):
        return self._obj_list[0] if self._obj_list else None

    def all(self):
        return self._obj_list

    def filter(self, expression):
        exp_list = expression.split('==')
        if len(exp_list) != 2:
            raise Exception(f'expression ({expression}) error')
        tag = exp_list[0].strip().split('.')[-1]
        value = exp_list[1].strip()

        filter_obj_list = list()
        for obj in self._obj_list:
            if obj.get(tag) and obj.get(tag) == value:
                filter_obj_list.append(obj)

        return filter_obj_list


class InfluxClient:

    def __init__(self):
        self._client = InfluxDBClient(url=cfg.CONF.influxdb.url,
                                      token=f'{cfg.CONF.influxdb.username}:{cfg.CONF.influxdb.password}',
                                      org=cfg.CONF.influxdb.organization)
        self._bucket = f'{cfg.CONF.influxdb.database}/{cfg.CONF.influxdb.retention_policy}'

    def _write(self, record):
        write_api = self._client.write_api(write_options=SYNCHRONOUS)
        write_api.write(bucket=self._bucket, record=record)
        LOG.debug('InfluxDB write record=%s to bucket=%s', record, self._bucket)
        write_api.__del__()

    def write(self, model):
        self._write(model.convert_to_point())

    def query(self, model):
        query_api = self._client.query_api()
        tables = query_api.query(query=f'from(bucket:"{self._bucket}")'
                                       f' |> range(start: 0, stop: now())'
                                       f' |> filter(fn: (r) => r._measurement == "{model.get_mea(model)}")')
        query_api.__del__()
        tags = model.get_tags(model)
        obj_list = list()
        obj = dict()
        delimeter_field = None
        for table in tables:
            for record in table.records:
                if not delimeter_field:
                    delimeter_field = record.get_field()
                if record.get_field() == delimeter_field and obj:
                    obj_list.append(obj)
                    obj = dict()
                for tag in tags:
                    if not obj.get(tag):
                        obj[tag] = record.values[tag]
                obj[record.get_field()] = record.get_value()
        if obj:
            obj_list.append(obj)

        return QueryObject(obj_list)


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
