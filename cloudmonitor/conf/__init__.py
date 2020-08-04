from oslo_config import cfg

from cloudmonitor._i18n import _

opts = [
    cfg.StrOpt('data_source', default='local_cache', help=_('The data source while RocketMQ send from.'))
]


def register_opts():
    cfg.CONF.register_opts(opts)
