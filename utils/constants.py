from pathlib import Path

# Status codes returned by functions
SUCCESS = 0
OTHER = 1
ERROR = -1

# Overall system states
RUNNING = 0
RECOVERABLE = 1
IRRECOVERABLE = -1

LOGGING_PATH = Path("/home/jb/PycharmProjects/Hue/logs")
ERROR_LOG_FILE = "JB_HUE_ERROR"
STANDARD_LOG_FILE = "JB_HUE"
LOG_FILE_FORMAT = "%(asctime)s, %(levelname)s, %(module)s.%(funcName)s@%(lineno)d,       %(message)s"
