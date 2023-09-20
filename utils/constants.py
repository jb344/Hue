import logging as __logging
from pathlib import Path as __Path

# Status codes returned by functions
SUCCESS = 0
OTHER = 1
ERROR = -1

# Overall system and thread states
RUNNING = 0
RECOVERABLE = 1
IRRECOVERABLE = -1

# Thread behaviour
KILL = -1

# Logging specific
LOGGING_PATH = __Path("/home/pi/Hue/logs")
ERROR_LOG_FILE = "HUE_ERROR"
STANDARD_LOG_FILE = "HUE"
LOG_FILE_FORMAT = __logging.Formatter("%(asctime)s, %(levelname)s, %(module)s.%(funcName)s()->%(lineno)d,       %(message)s")

# Number of days in a week
DAYS_IN_WEEK = 7
# Check the the season every Monday
DAY_OF_WEEK_TO_CHECK_SEASON = 1

# Seasons determined by their months
WINTER_MONTHS = [12, 1, 2]          # Dec, Jan, Feb
SPRING_MONTHS = [3, 4, 5]           # Mar, Apr, May
SUMMER_MONTHS = [6, 7, 8]           # Jun, Jul, Aug
AUTUMN_MONTHS = [9, 10, 11]         # Sep, Oct, Nov
