import os

log = __import__("logger.py").Logger.LOGGER


def test_and_mkdir(directory):
    """
        Test if a directory exists, if not, make it
            :param directory:       Directory to test/make
            :return:                ERROR on failure, SUCCESS on success
    """
    try:
        if not os.path.exists(directory):
            os.mkdir(directory)
            if not os.path.exists(directory) and os.path.isdir(directory):
                log.warning("The following directory could not be made; {}".format(directory))
    except Exception as err:
        log.exception(err)

