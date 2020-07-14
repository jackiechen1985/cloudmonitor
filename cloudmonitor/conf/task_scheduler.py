from oslo_config import cfg

from cloudmonitor._i18n import _

opts = [
    cfg.StrOpt('task_conf_path',
               help=_('The configuration path of task.json.'))
]


def register_opts():
    cfg.CONF.register_opts(opts, 'task_scheduler')
