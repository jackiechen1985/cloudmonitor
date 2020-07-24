import logging

from oslo_config import cfg
from oslo_concurrency import lockutils

from influxdb_client import InfluxDBClient
from influxdb_client.client.write_api import SYNCHRONOUS

from cloudmonitor.conf import influx

LOG = logging.getLogger(__name__)
formatter = logging.Formatter('%(asctime)s %(process)d %(levelname)s %(name)s [-] %(message)s')
file_handler = logging.FileHandler("/var/log/cloudmonitor/influx.log")
file_handler.setFormatter(formatter)
LOG.addHandler(file_handler)

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

        return QueryObject(filter_obj_list)

    def order_by(self, expression):
        exp_list = expression.split('.')
        sort = exp_list[-1].strip()
        if sort == 'asc':
            reverse = False
        elif sort == 'desc':
            reverse = True
        else:
            raise Exception(f'sort ({sort}) not support, only asc or desc is allowed')
        tag = exp_list[-2].strip()
        self._obj_list.sort(key=lambda x: x[tag], reverse=reverse)


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

        # Find all records count
        obj_list = list()
        influx_record_time_list = list()
        for table in tables:
            for record in table.records:
                influx_record_time = record.get_time()
                if influx_record_time not in influx_record_time_list:
                    influx_record_time_list.append(influx_record_time)
                    obj = dict()
                    obj['influx_record_time'] = influx_record_time
                    obj_list.append(obj)

        tags = model.get_all_tags(model)
        for table in tables:
            for record in table.records:
                obj = obj_list[influx_record_time_list.index(record.get_time())]
                for tag in tags:
                    if not obj.get(tag):
                        obj[tag] = record.values[tag]
                obj[record.get_field()] = record.get_value()

        # Sort obj_list base on influx timestamp
        obj_list.sort(key=lambda x: x['influx_record_time'])
        for obj in obj_list:
            obj.pop('influx_record_time')

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
