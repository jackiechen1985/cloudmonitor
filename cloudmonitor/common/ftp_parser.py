from oslo_log import log as logging

LOG = logging.getLogger(__name__)


class FtpParser:

    @staticmethod
    def parse_to_list(file_path):
        records = []
        with open(file_path, 'r') as fp:
            while True:
                line = fp.readline()
                if not line:
                    break
                line = line[0:-1]
                # LOG.debug('ftp line in file (%s): %s', file_path, line)
                fields = line.split(';')
                records.append(fields)
        return records
