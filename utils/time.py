import datetime
from .constants import *


def get_current_time(log=None):
    """
        Get the current date/time, in the format; 120220_183800
            :param log      Logger to attempt to use, this can be None
            :return:        The current date/time, in the format; 120220_183800, or None
    """
    now = None
    try:
        now = datetime.datetime.now().strftime("%d%m%y_%H%M%S")
    except Exception as err:
        if log is not None and log != ERROR:
            log.exception(err)
        else:
            print(err)

    return now

