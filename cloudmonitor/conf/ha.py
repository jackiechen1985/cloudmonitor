from oslo_config import cfg

from cloudmonitor._i18n import _

opts = [
    cfg.BoolOpt('enable',
                default=False,
                help=_('Http url for accessing InfluxDB.')),
    cfg.StrOpt('host_ip',
               help=_('Host ip address.')),
    cfg.StrOpt('vip',
               help=_('Virtual ip address for HA.'))
]


def register_opts():
    cfg.CONF.register_opts(opts, 'high_availability')
