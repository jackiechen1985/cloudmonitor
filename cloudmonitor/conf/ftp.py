from oslo_config import cfg

from cloudmonitor._i18n import _

opts = [
    cfg.StrOpt('host',
               help=_('ftp server ip address.')),
    cfg.IntOpt('port',
               default=21,
               help=_('ftp server port.')),
    cfg.IntOpt('connection_timeout',
               default=60,
               help=_('ftp server connection timeout.')),
    cfg.StrOpt('username',
               help=_('Username for ftp server.')),
    cfg.StrOpt('password',
               help=_('Password for ftp server.')),
    cfg.StrOpt('nat_dir',
               help=_('Remote nat directory in ftp server.')),
    cfg.StrOpt('ipsec_dir',
               help=_('Remote ipsec directory in ftp server.')),
    cfg.StrOpt('vlb_dir',
               help=_('Remote loadbalancer directory in ftp server.')),
    cfg.StrOpt('vlistener_dir',
               help=_('Remote loadbalancer listener directory in ftp server.'))
]


def register_opts():
    cfg.CONF.register_opts(opts, 'ftp')
