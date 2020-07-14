import sys
from cloudmonitor import version

from oslo_config import cfg
from oslo_log import log as logging

from cloudmonitor._i18n import _

LOG = logging.getLogger(__name__)

logging.register_options(cfg.CONF)


def init(args, **kwargs):
    cfg.CONF(args=args, project='cloudmonitor',
             version='%%(prog)s %s' % version.version_info.release_string(),
             **kwargs)


def setup_logging():
    logging.set_defaults(default_log_levels=logging.get_default_log_levels())
    logging.setup(cfg.CONF, 'cloudmonitor')
    LOG.info('Logging enabled!')
    LOG.info('%(prog)s version %(version)s',
             {'prog': sys.argv[0],
              'version': version.version_info.release_string()})
    LOG.debug('command line: %s', ' '.join(sys.argv))


def init_configuration():
    # the configuration will be read into the cfg.CONF global data structure
    init(sys.argv[1:])
    setup_logging()
    if not cfg.CONF.config_file:
        sys.exit(_("ERROR: Unable to find configuration file via the default"
                   " search paths (~/.cloudmonitor/, ~/, /etc/cloudmonitor/, /etc/) and"
                   " the '--config-file' option!"))
