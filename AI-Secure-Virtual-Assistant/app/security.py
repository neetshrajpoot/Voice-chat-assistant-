import logging
from pathlib import Path


LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

LOG_FILE = LOG_DIR / "assistant.log"


logger = logging.getLogger("secure_assistant")
logger.setLevel(logging.INFO)
logger.propagate = False

if not logger.handlers:
    handler = logging.FileHandler(
        LOG_FILE,
        encoding="utf-8"
    )

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(message)s"
    )

    handler.setFormatter(formatter)
    logger.addHandler(handler)


def log_event(event: str):
    logger.info(event)

def log_command_received():
    log_event("COMMAND_RECEIVED")


def log_intent_detected(intent: str, confidence: float):
    log_event(
        f"INTENT_DETECTED | intent={intent} | confidence={confidence}"
    )


def log_tool_allowed(tool_name: str):
    log_event(f"TOOL_ALLOWED | tool={tool_name}")


def log_tool_blocked(tool_name: str):
    log_event(f"TOOL_BLOCKED | tool={tool_name}")


def log_response_generated():
    log_event("RESPONSE_GENERATED")