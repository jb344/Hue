import os

# Defined by me
from .constants import *


def test_and_mkdir(directory) -> Exception or int:
    """
        Test if a directory exists, if not, make it
            :param directory:       Directory to test/make
            :return:                Exception with traceback details on failure, SUCCESS on success
    """
    try:
        if not os.path.exists(directory):
            os.mkdir(directory)
            if not os.path.exists(directory):
                raise RuntimeError("Failed making the directory; {}".format(directory))
            elif not os.path.isdir(directory):
                raise NotADirectoryError("Failed making the directory; {}".format(directory))

        return SUCCESS
    except Exception as err:
        return err.with_traceback()

