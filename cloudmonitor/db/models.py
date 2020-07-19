from enum import Enum

import sqlalchemy as sa

from cloudmonitor.db.model_base import BASE


class SubTaskStatus(Enum):
    RUNNING = 'RUNNING'
    SUCCESS = 'SUCCESS'
    ERROR = 'ERROR'
    IDLE = 'IDLE'


class FtpStatus(Enum):
    DOWNLOAD_SUCCESS = 'DOWNLOAD_SUCCESS'
    SEND_SUCCESS = 'SEND_SUCCESS'
    SEND_ERROR = 'SEND_ERROR'


class FtpProducerDataSource(Enum):
    LOCAL_CACHE = 'LOCAL_CACHE'
    INFLUXDB = 'INFLUXDB'


class Task(BASE):
    id = sa.Column(sa.Integer, nullable=False, primary_key=True, autoincrement=True)
    name = sa.Column(sa.String(255), nullable=False, unique=True)
    type = sa.Column(sa.String(32), nullable=False)
    interval = sa.Column(sa.Integer, nullable=True)
    initial_delay = sa.Column(sa.Integer, nullable=True)
    module = sa.Column(sa.String(4096), nullable=False, unique=True)


class SubTask(BASE):
    id = sa.Column(sa.Integer, nullable=False, primary_key=True, autoincrement=True)
    start_time = sa.Column(sa.String(32), nullable=False)
    end_time = sa.Column(sa.String(32), nullable=False)
    status = sa.Column(sa.String(32), nullable=False)
    description = sa.Column(sa.String(4096), nullable=True)
    host_ip = sa.Column(sa.String(16), nullable=False)
    task_id = sa.Column(sa.Integer, sa.ForeignKey('tasks.id', ondelete='CASCADE'), primary_key=True)


class Ftp(BASE):
    id = sa.Column(sa.Integer, nullable=False, primary_key=True, autoincrement=True)
    host = sa.Column(sa.String(16), nullable=False)
    name = sa.Column(sa.String(255), nullable=False, unique=True)
    size = sa.Column(sa.BigInteger(), nullable=False)
    mtime = sa.Column(sa.String(32), nullable=False)
    remote_dir = sa.Column(sa.String(4096), nullable=False)
    local_file_path = sa.Column(sa.String(4096), nullable=False)
    status = sa.Column(sa.String(32), nullable=False)
    subtask_id = sa.Column(sa.Integer, sa.ForeignKey('subtasks.id', ondelete='CASCADE'), primary_key=True)


class FtpRemoteDir(BASE):
    host = sa.Column(sa.String(16), nullable=False, primary_key=True)
    remote_dir = sa.Column(sa.String(4096), nullable=False, primary_key=True)
    mtime = sa.Column(sa.String(32), nullable=False)


class FtpProducer(BASE):
    id = sa.Column(sa.Integer, nullable=False, primary_key=True, autoincrement=True)
    time = sa.Column(sa.String(32), nullable=False)
    data_source = sa.Column(sa.String(32), nullable=False)
    subtask_id = sa.Column(sa.Integer, sa.ForeignKey('subtasks.id', ondelete='CASCADE'), primary_key=True)
    ftp_id = sa.Column(sa.Integer, sa.ForeignKey('ftps.id', ondelete='CASCADE'), primary_key=True)
