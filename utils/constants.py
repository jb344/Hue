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

# Logging specific crap
LOGGING_PATH = __Path("./logs")
ERROR_LOG_FILE = "JB_HUE_ERROR"
STANDARD_LOG_FILE = "JB_HUE"
LOG_FILE_FORMAT = __logging.Formatter("%(asctime)s, %(levelname)s, %(module)s.%(funcName)s()->%(lineno)d,       %(message)s")
