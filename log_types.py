from enum import Enum
from colors import TEXT_LIGHT, GREEN, AMBER, RED, DARK_ORANGE, BLUE, PURPLE


class LogType(Enum):
    INFO    = TEXT_LIGHT
    SUCCESS = GREEN
    WARNING = AMBER
    ERROR   = RED
    ALERT   = DARK_ORANGE
    DEBUG   = BLUE
    ACUM    = PURPLE