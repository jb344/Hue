import datetime

# Defined by me
from .constants import *


def get_current_date_time(logger=None) -> str:
    """
        Get the current date/time, in the format; 120220_183800
            :param logger       Logger to attempt to use, this can be None
            :return:            The current date/time, in the format; 120220_183800, or None
    """
    now = None
    try:
        now = datetime.datetime.now().strftime("%d%m%y_%H%M%S")
    except Exception as err:
        if logger is not None and logger != ERROR:
            logger.exception(err)
        else:
            print(err)
    return now


def get_current_time(logger=None) -> tuple:
    """
        Get the current time
            :param logger:      Logger to log to
            :return:            hour, minute, seconds, as ints, or None if failure occurs
    """
    hour, minute, second = None, None, None
    try:
        time_now = datetime.datetime.now()
        hour, minute, second = time_now.hour, time_now.minute, time_now.second
    except Exception as err:
        if logger is not None and logger != ERROR:
            logger.exception(err)
        else:
            print(err)
    return hour, minute, second


def get_current_hour(logger=None) -> int:
    """
        Get the current hour
            :param logger:      Logger to log to
            :return:            hour as a 24 hour int
    """
    try:
        return datetime.datetime.now().hour
    except Exception as err:
        if logger is not None and logger != ERROR:
            logger.exception(err)
        else:
            print(err)


def get_current_weekday(logger=None) -> int:
    """
            Get the current weekday
                :param logger:      Logger to log to
                :return:            weekday as a 1-7 int (1 = Monday, 7 = Sunday)
        """
    try:
        return datetime.datetime.today().isoweekday()
    except Exception as err:
        if logger is not None and logger != ERROR:
            logger.exception(err)
        else:
            print(err)


def get_current_month(logger=None) -> int:
    """
            Get the current month
                :param logger:      Logger to log to
                :return:            month as a 1-12 int
        """
    try:
        return datetime.datetime.now().month
    except Exception as err:
        if logger is not None and logger != ERROR:
            logger.exception(err)
        else:
            print(err)
