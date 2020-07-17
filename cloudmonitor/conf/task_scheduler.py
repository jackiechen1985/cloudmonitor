from oslo_config import cfg

from cloudmonitor._i18n import _

opts = [
    cfg.StrOpt('task_conf_path',
               help=_('The configuration path of task.json.')),
    cfg.IntOpt('max_subtask',
               default=10000,
               help=_('Max subtask count. If current subtask count larger than max_subtask, '
                      ' then garbage_clean task will start to clean subtask'))
]


def register_opts():
    cfg.CONF.register_opts(opts, 'task_scheduler')
