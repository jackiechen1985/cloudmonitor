import os

from ftplib import FTP
from sqlalchemy import and_

from oslo_log import log as logging

from cloudmonitor.db import models

LOG = logging.getLogger(__name__)

local_cache_dir = '/var/lib/cloudmonitor/ftp'
if not os.path.exists(local_cache_dir):
    try:
        os.makedirs(local_cache_dir)
    except Exception as e:
        LOG.error(e)


class FtpClient:

    def __init__(self, context, host, port, connection_timeout, username, password):
        self._client = FTP()
        self._context = context
        self._host = host
        self._port = port
        self._connection_timeout = connection_timeout
        self._username = username
        self._password = password

    def connect(self):
        self._client.set_debuglevel(2)
        try:
            self._client.connect(self._host, self._port, self._connection_timeout)
            self._client.login(self._username, self._password)
        except Exception as e:
            LOG.error('Connect ftp server error: host=%s, port=%d, connection_timeout=%d, username=%s, password=%s',
                      self._host, self._port, self._connection_timeout, self._username, self._password)
            raise e
        LOG.info('Successfully login ftp server: host=%s, port=%d, connection_timeout=%d, username=%s, password=%s',
                 self._host, self._port, self._connection_timeout, self._username, self._password)
        return self._client

    def quit(self):
        self._client.quit()

    def change_remote_dir(self, remote_dir):
        self._client.cwd(remote_dir)

    def _check_update_file_list(self):
        file_list = self._client.nlst()
        update_file_list = []
        db_ftp_remote_dir = self._context.session.query(models.FtpRemoteDir).filter(
            and_(models.FtpRemoteDir.host == self._host, models.FtpRemoteDir.remote_dir == self._client.pwd())).first()
        for file in file_list:
            db_ftp = self._context.session.query(models.Ftp).filter(models.Ftp.name == file).first()
            if not db_ftp:
                if not db_ftp_remote_dir:
                    update_file_list.append(file)
                else:
                    t = self._client.sendcmd(f'MDTM {file}').split(' ')[1]
                    mtime = f'{t[0:4]}-{t[4:6]}-{t[6:8]} {t[8:10]}:{t[10:12]}:{t[12:14]}'
                    if mtime > db_ftp_remote_dir.mtime:
                        update_file_list.append(file)
        LOG.info('Update file list: %s', update_file_list)
        return update_file_list

    def _retrieve_file_list(self, file_list):
        with self._context.session.begin(subtransactions=True):
            remote_dir = self._client.pwd()
            latest_mtime = None

            for file in file_list:
                local_file_path = os.path.join(local_cache_dir, file)
                with open(local_file_path, 'wb') as fp:
                    self._client.retrbinary('RETR ' + file, fp.write, 1024)
                    LOG.info('Retrieve file (%s) to local cache: %s', file, local_cache_dir)

                size = self._client.sendcmd(f'SIZE {file}').split(' ')[1]
                LOG.info('Retrieve file (%s) size: %s', file, size)

                t = self._client.sendcmd(f'MDTM {file}').split(' ')[1]
                mtime = f'{t[0:4]}-{t[4:6]}-{t[6:8]} {t[8:10]}:{t[10:12]}:{t[12:14]}'
                LOG.info('Retrieve file (%s) mtime: %s', file, mtime)
                if latest_mtime:
                    if mtime > latest_mtime:
                        latest_mtime = mtime
                else:
                    latest_mtime = mtime

                db_ftp = models.Ftp(host=self._host, name=file, size=size, mtime=mtime, remote_dir=remote_dir,
                                    local_file_path=local_file_path, status=models.FtpStatus.DOWNLOAD_SUCCESS.value,
                                    subtask_id=self._context.subtask_id)
                self._context.session.add(db_ftp)

            if latest_mtime:
                db_ftp_remote_dir = self._context.session.query(models.FtpRemoteDir).filter(
                    and_(models.FtpRemoteDir.host == self._host,
                         models.FtpRemoteDir.remote_dir == remote_dir)).first()
                if db_ftp_remote_dir:
                    db_ftp_remote_dir.update({
                        'mtime': latest_mtime
                    })
                else:
                    db_ftp_remote_dir = models.FtpRemoteDir(host=self._host, remote_dir=remote_dir, mtime=latest_mtime)
                    self._context.session.add(db_ftp_remote_dir)

            self._context.session.flush()

    def sync_file_to_local_cache(self):
        update_file_list = self._check_update_file_list()
        self._retrieve_file_list(update_file_list)

    def get_ftp_list_by_subtask_id(self, subtask_id):
        ftp_list = self._context.session.query(models.Ftp).filter(models.Ftp.subtask_id == subtask_id).all()
        return ftp_list
