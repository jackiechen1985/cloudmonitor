from oslo_config import cfg

from cloudmonitor._i18n import _

opts = [
    cfg.StrOpt('namesrv_addr',
               help=_('RocketMQ nameserver address')),
    cfg.StrOpt('producer_group',
               help=_('RocketMQ producer group.')),
    cfg.StrOpt('cm_topic',
               help=_('RocketMQ configure topic.')),
    cfg.StrOpt('pm_topic',
               help=_('RocketMQ performance topic.'))
]


def register_opts():
    cfg.CONF.register_opts(opts, 'rocketmq')
