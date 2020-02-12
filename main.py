import logging
from utils.logger import Logger
from utils.constants import *


if __name__ == "__main__":
    system_state = RECOVERABLE
    log = __import__("utils.logger").Logger.LOGGER

    try:
        # Attempt to create a logger object so we can have some debug files!
        Logger.configure_log(__name__)

        # Check that the logs were created before getting excited and initialising the system
        if log is not None and log != ERROR:
            system_state = RUNNING
        else:
            raise RuntimeError("Failed creating logs...")

    except Exception as e:
        if log is not None and log != ERROR:
            log.exception(e)
            logging.shutdown()
            exit(ERROR)

    logging.shutdown()
    exit(SUCCESS)
