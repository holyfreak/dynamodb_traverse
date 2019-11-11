import logging
import sys
from os.path import expanduser


class Base(object):

    def __init__(self, **kwargs):
        self._setup_logging(self, **kwargs)

    @staticmethod
    def _setup_logging(self, log_to_screen=False, **kwargs):
        for handler in logging.root.handlers[:]:
            logging.root.removeHandler(handler)
        # log setup
        log_location = kwargs.pop("log_path", '/'.join((expanduser('~'), 'logs/pyacm', 'general.log')))
        logger_name = kwargs.pop("name", "base_logger")

        formatter = logging.Formatter(fmt='%(asctime)s %(levelname)-8s %(message)s',
                                      datefmt='%Y-%m-%d %H:%M:%S')
        handler = logging.FileHandler(log_location, mode='w')
        handler.setFormatter(formatter)

        logger = logging.getLogger(logger_name)
        logger.setLevel(logging.INFO)
        logger.addHandler(handler)
        if log_to_screen:
            screen_handler = logging.StreamHandler(stream=sys.stdout)
            screen_handler.setFormatter(formatter)
            logger.addHandler(screen_handler)

        # logging.basicConfig(filename=log_location, level=logging.INFO)
        self.logger = logger


    def info(self, msg):
        self.logger.info(msg)

    def error(self, msg):
        self.logger.error(msg)
