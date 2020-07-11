from enum import Enum

import sqlalchemy as sa

from cloudmonitor.db.model_base import BASE


# Subtask status
class SubTaskStatus(Enum):
    CREATE = 'CREATE'
    RUNNING = 'RUNNING'
    SUCCESS = 'SUCCESS'
    ERROR = 'ERROR'


SUBTASK_CREATE = 'CREATE'
SUBTASK_RUNNING = 'RUNNING'
SUBTASK_SUCCESS = 'SUCCESS'
SUBTASK_ERROR = 'ERROR'


class Task(BASE):
    id = sa.Column(sa.Integer, nullable=False, primary_key=True, autoincrement=True)
    name = sa.Column(sa.String(256), nullable=False, unique=True)
    type = sa.Column(sa.String(32), nullable=False)
    interval = sa.Column(sa.Integer, nullable=True)
    initial_delay = sa.Column(sa.Integer, nullable=True)
    module = sa.Column(sa.String(512), nullable=False)


class SubTask(BASE):
    id = sa.Column(sa.Integer, nullable=False, primary_key=True, autoincrement=True)
    start_time = sa.Column(sa.String(32), nullable=False)
    end_time = sa.Column(sa.String(32), nullable=False)
    status = sa.Column(sa.String(32), nullable=False)
    description = sa.Column(sa.String(512), nullable=True)
    task_id = sa.Column(sa.Integer, sa.ForeignKey('tasks.id', ondelete="CASCADE"), primary_key=True)


class Ftp(BASE):
    id = sa.Column(sa.Integer, nullable=False, primary_key=True, autoincrement=True)
    host = sa.Column(sa.String(16), nullable=False)
    name = sa.Column(sa.String(255), nullable=False, unique=True)
    size = sa.Column(sa.BigInteger(), nullable=False)
    mtime = sa.Column(sa.String(32), nullable=False)
    local_file_path = sa.Column(sa.String(255), nullable=False)
    subtask_id = sa.Column(sa.Integer, sa.ForeignKey('subtasks.id', ondelete="CASCADE"), primary_key=True)
