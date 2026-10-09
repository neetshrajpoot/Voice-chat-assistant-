from app.tools.applications import open_application
from app.tools.browser import (
    search_web,
    search_youtube,
    open_youtube,
)
from app.tools.calculator import calculate

from app.security import (
    log_tool_allowed,
    log_tool_blocked,
)


TOOLS = {
    "open_application": open_application,
    "web_search": search_web,
    "youtube_search": search_youtube,
    "open_youtube": open_youtube,
    "calculate": calculate,
}


ALLOWED_TOOLS = {
    "open_application",
    "web_search",
    "youtube_search",
    "open_youtube",
    "calculate",
}


def execute_tool(tool_name: str, **kwargs):
    """
    Execute only explicitly allowed assistant tools.
    """

    if tool_name not in ALLOWED_TOOLS:
        log_tool_blocked(tool_name)

        return (
            "Security blocked: "
            "this tool is not allowed."
        )

    tool = TOOLS.get(tool_name)

    if tool is None:
        log_tool_blocked(tool_name)

        return (
            "Security blocked: "
            "tool is unavailable."
        )

    log_tool_allowed(tool_name)

    try:
        return tool(**kwargs)

    except Exception:
        return (
            "The requested tool failed safely."
        )