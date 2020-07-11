#!/usr/bin/python3

import datetime
import json

from oslo_config import cfg
from oslo_log import log as logging
from oslo_service import service
from oslo_utils import importutils

from cloudmonitor._i18n import _
from cloudmonitor.conf import task_scheduler as ts
from cloudmonitor.task import PeriodicTask
from cloudmonitor.context import get_context
from cloudmonitor.db import models

LOG = logging.getLogger(__name__)

ts.register_opts()


class TaskScheduler:

    def __init__(self):
        with open(cfg.CONF.task_scheduler.task_conf_path, 'r') as fp:
            self.tasks = json.loads(fp.read())
            if len(self.tasks) < 1:
                LOG.error('No task found')
                raise Exception(_('No task found'))
            else:
                LOG.info(_('Found task: %s from %s'), self.tasks, cfg.CONF.task_scheduler.task_conf_path)
        self.process_launcher = service.ProcessLauncher(cfg.CONF, wait_interval=1.0)

    def start(self):
        for task in self.tasks:
            if task['type'] != 'periodic':
                LOG.error('%s not supported yet', task['type'])
                raise RuntimeError(_('%s not supported yet' % task['type']))
            else:
                task['context'] = get_context()
                task['id'] = self._sync_database(task)
                periodic_task = PeriodicTask(task['interval'], task['initial_delay'], self.run, task)
                self.process_launcher.launch_service(periodic_task, 1)
                LOG.info('Start a new task with name: %s, type: %s, interval: %s, initial_delay: %s, module: %s',
                         task['name'], task['type'], task['interval'], task['initial_delay'], task['module'])

        self.process_launcher.wait()

    @staticmethod
    def _sync_database(task):
        session = task['context'].session
        with session.begin(subtransactions=True):
            db_task = session.query(models.Task).filter(models.Task.name == task['name']).first()
            if db_task:
                db_task.update({
                    'type': task['type'],
                    'interval': task['interval'],
                    'initial_delay': task['initial_delay'],
                    'module': task['module']
                })
            else:
                db_task = models.Task(name=task['name'], type=task['type'], interval=task['interval'],
                                      initial_delay=task['initial_delay'], module=task['module'])
                session.add(db_task)
                session.flush()

        return db_task.id

    @staticmethod
    def run(task):
        subtask_class = importutils.import_class(task['module'])
        subtask = subtask_class()
        if not subtask.run_supported():
            LOG.error('%s does not implement run method', task['module'])
            raise NotImplementedError()

        context = task['context']
        with context.session.begin(subtransactions=True):
            db_subtask = models.SubTask(start_time=datetime.datetime.now().strftime('%b-%d-%Y %H:%M:%S'),
                                        end_time='',
                                        status=models.SubTaskStatus.RUNNING.value,
                                        task_id=task['id'])
            context.session.add(db_subtask)
            context.session.flush()
        context.subtask_id = db_subtask.id

        try:
            subtask.run(context)
            db_subtask.update({
                'end_time': datetime.datetime.now().strftime('%b-%d-%Y %H:%M:%S'),
                'status': models.SubTaskStatus.SUCCESS.value
            })
            context.session.flush()
        except Exception as e:
            db_subtask.update({
                'end_time': datetime.datetime.now().strftime('%b-%d-%Y %H:%M:%S'),
                'status': models.SubTaskStatus.ERROR.value,
                'description': str(e)
            })
            context.session.flush()
            LOG.error(e)
