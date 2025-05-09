from enum import Enum

class Detail(str, Enum):
    low    = "low"
    medium = "medium"
    high   = "high"

DEFAULT_MODEL = 'gpt-4o-mini'
DEFAULT_MAX_QUESTIONS = 10