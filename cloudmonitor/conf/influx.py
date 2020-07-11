from oslo_config import cfg

from cloudmonitor._i18n import _

opts = [
    cfg.StrOpt('url',
               help=_('Http url for accessing InfluxDB.')),
    cfg.StrOpt('username',
               help=_('Username for InfluxDB.')),
    cfg.StrOpt('password',
               help=_('Password for InfluxDB.')),
    cfg.StrOpt('database',
               help=_('Database name')),
    cfg.StrOpt('retention_policy',
               help=_('Retention policy.')),
    cfg.StrOpt('organization',
               help=_('Organization name (used as a default in query and write API)'))
]


def register_opts():
    cfg.CONF.register_opts(opts, 'influxdb')
