import os

from sqlalchemy import func, and_

from oslo_config import cfg
from oslo_log import log as logging

from cloudmonitor.conf import task_scheduler as ts
from cloudmonitor.subtasks.subtask_base import SubTaskBase
from cloudmonitor.db import models

LOG = logging.getLogger(__name__)

ts.register_opts()


class GarbageClean(SubTaskBase):

    def run(self, context):
        status = models.SubTaskStatus.IDLE.value

        subtask_count = context.session.query(func.count(models.SubTask.id)).scalar()
        if subtask_count > cfg.CONF.task_scheduler.max_subtask:
            LOG.info('Start to clean subtask in %s status: count=%d', models.SubTaskStatus.IDLE.value, subtask_count)
            with context.session.begin(subtransactions=True):
                db_subtask = context.session.query(models.SubTask).filter(
                    models.SubTask.status == models.SubTaskStatus.IDLE.value).all()
                for subtask in db_subtask:
                    context.session.delete(subtask)
                    LOG.info('Delete subtask in %s status with id: %d', models.SubTaskStatus.IDLE.value, subtask.id)
                context.session.flush()
            status = models.SubTaskStatus.SUCCESS.value

        subtask_count = context.session.query(func.count(models.SubTask.id)).scalar()
        if subtask_count > cfg.CONF.task_scheduler.max_subtask:
            LOG.info('Start to clean subtask in %s status: count=%d', models.SubTaskStatus.SUCCESS.value, subtask_count)
            with context.session.begin(subtransactions=True):
                db_subtask = context.session.query(models.SubTask).join(models.Ftp).filter(
                    and_(models.SubTask.status == models.SubTaskStatus.SUCCESS.value,
                         models.Ftp.status == models.FtpStatus.SEND_SUCCESS.value)).limit(
                    cfg.CONF.task_scheduler.max_subtask / 2).all()
                for subtask in db_subtask:
                    db_ftp = context.session.query(models.Ftp).filter(models.Ftp.subtask_id == subtask.id)
                    for ftp in db_ftp:
                        if os.path.exists(ftp.local_file_path):
                            os.unlink(ftp.local_file_path)
                            LOG.info('Delete ftp local cache: %s', ftp.local_file_path)
                    context.session.delete(subtask)
                    LOG.info('Delete subtask in %s status with id: %d', models.SubTaskStatus.SUCCESS.value, subtask.id)
                context.session.flush()
            status = models.SubTaskStatus.SUCCESS.value

        return status, None
