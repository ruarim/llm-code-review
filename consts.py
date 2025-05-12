from enum import Enum

class Detail(str, Enum):
    low    = "low"
    medium = "medium"
    high   = "high"

DEFAULT_MODEL = 'gpt-4o-mini'
DEFAULT_MAX_QUESTIONS = 10

TRANSCRIPT_HEADERS = {
    "document": "# AI Code Review",
    "review": "## Review",
    "diff": "## Diff reviewed",
    "usage": "## Usage",
    "context": "## ADDITIONAL CONTEXT",
}
