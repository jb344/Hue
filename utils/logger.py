import logging
from logging.handlers import RotatingFileHandler
from .constants import *
from .time import get_current_time


class ErrorFilter(logging.Filter):
    """
        Class that overrides logging.Filter, so that we can return True if the provided record to log is of level
        ERROR or CRITICAL
    """
    def filter(self, record):
        return record.levelname == logging.ERROR or record.levelname == logging.CRITICAL


class StandardFilter(logging.Filter):
    """
        Class that overrides logging.Filter, so that we can return True if the provided record to log is of level
        DEBUG, INFO or WARNING
    """
    def filter(self, record):
        return record.levelname != logging.ERROR and record.levelname != logging.CRITICAL


class Logger:
    LOGGER = None

    def configure_log(self, name):
        """
            Configure a logger, for logging DEBUG, INFO, and WARN message to one file, and ERR, and CRIT to a different
            file
                :param name:        Name of the logger object, we usually just pass in the name of the calling file
                :return:            ERROR on failure, logger object on success
        """
        try:
            logger = logging.getLogger(name)

            # Create a rotating file handler that rotates every 50MB, and stores only the last 5 logs, aka 250MB of data
            error_handler = RotatingFileHandler(
                filename=LOGGING_PATH.joinpath(ERROR_LOG_FILE + "_{}.log".format(get_current_time())),
                mode="w+", maxBytes=52430000, backupCount=5, encoding="ISO8859-1")
            standard_handler = RotatingFileHandler(
                filename=LOGGING_PATH.joinpath(STANDARD_LOG_FILE + "_{}.log".format(get_current_time())),
                mode="w+", maxBytes=52430000, backupCount=5, encoding="ISO8859-1")

            # Specify the format of the log files
            error_handler.setFormatter(LOG_FILE_FORMAT)
            standard_handler.setFormatter(LOG_FILE_FORMAT)

            # Add filters to our handlers so only DEBUG, INFO, and WARN go to the standard log file, while ERR, and CRIT go to
            # the error file
            error_handler.addFilter(ErrorFilter)
            standard_handler.addFilter(StandardFilter)

            # Add the handlers to our logger so they actually get used
            logger.addHandler(error_handler)
            logger.addHandler(standard_handler)

            # Override the default logging level of WARN, so we will get DEBUG and INFO messages out
            logger.setLevel(logging.DEBUG)

            # Set the class field to our new logger
            self.LOGGER = logger
        except Exception as err:
            print(err)
            return ERROR
