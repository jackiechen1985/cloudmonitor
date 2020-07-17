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

        # Clean all clean subtask
        subtask_count = context.session.query(func.count(models.SubTask.id)).scalar()
        if subtask_count > cfg.CONF.task_scheduler.max_subtask:
            LOG.info('Total task (%d) exceed max_subtask (%d), start to clean all garbage clean subtask',
                     subtask_count, cfg.CONF.task_scheduler.max_subtask)
            with context.session.begin(subtransactions=True):
                db_subtask = context.session.query(models.SubTask).join(models.Task).filter(
                    models.Task.name == GarbageClean.__name__).all()
                for subtask in db_subtask:
                    context.session.delete(subtask)
                    LOG.info('Delete garbage clean subtask with id: %d', subtask.id)
                context.session.flush()
            status = models.SubTaskStatus.SUCCESS.value

        # Clean all idle subtask
        subtask_count = context.session.query(func.count(models.SubTask.id)).scalar()
        if subtask_count > cfg.CONF.task_scheduler.max_subtask:
            LOG.info('Total task (%d) exceed max_subtask (%d), Start to clean subtask in %s status',
                     subtask_count, cfg.CONF.task_scheduler.max_subtask, models.SubTaskStatus.IDLE.value)
            with context.session.begin(subtransactions=True):
                db_subtask = context.session.query(models.SubTask).filter(
                    models.SubTask.status == models.SubTaskStatus.IDLE.value).all()
                for subtask in db_subtask:
                    context.session.delete(subtask)
                    LOG.info('Delete subtask in %s status with id: %d', models.SubTaskStatus.IDLE.value, subtask.id)
                context.session.flush()
            status = models.SubTaskStatus.SUCCESS.value

        # Clean all send sucess subtask
        subtask_count = context.session.query(func.count(models.SubTask.id)).scalar()
        if subtask_count > cfg.CONF.task_scheduler.max_subtask:
            LOG.info('Total task (%d) exceed max_subtask (%d), Start to clean subtask in %s status',
                     subtask_count, cfg.CONF.task_scheduler.max_subtask, models.SubTaskStatus.SUCCESS.value)
            with context.session.begin(subtransactions=True):
                db_collector_subtask = context.session.query(models.SubTask).join(models.Ftp).filter(
                    and_(models.SubTask.status == models.SubTaskStatus.SUCCESS.value,
                         models.Ftp.status == models.FtpStatus.SEND_SUCCESS.value)).all()
                for collector_subtask in db_collector_subtask:
                    db_ftp_producer = context.session.query(models.FtpProducer).join(models.Ftp).filter(
                        models.Ftp.subtask_id == collector_subtask.id).first()
                    if db_ftp_producer:
                        db_ftp_producer_subtask = context.session.query(models.SubTask).filter(
                            models.SubTask.id == db_ftp_producer.subtask_id).first()
                        if db_ftp_producer_subtask:
                            context.session.delete(db_ftp_producer_subtask)
                            LOG.info('Delete subtask in %s status with id: %d', models.SubTaskStatus.SUCCESS.value,
                                     db_ftp_producer_subtask.id)

                    db_ftp = context.session.query(models.Ftp).filter(models.Ftp.subtask_id == collector_subtask.id)
                    for ftp in db_ftp:
                        if os.path.exists(ftp.local_file_path):
                            os.unlink(ftp.local_file_path)
                            LOG.info('Delete ftp local cache: %s', ftp.local_file_path)
                    context.session.delete(collector_subtask)
                    LOG.info('Delete subtask in %s status with id: %d', models.SubTaskStatus.SUCCESS.value,
                             collector_subtask.id)
                context.session.flush()
            status = models.SubTaskStatus.SUCCESS.value

        return status, None
