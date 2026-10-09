from datetime import datetime

from app.intent import detect_intent
from app.tool_manager import execute_tool
from app.llm import ask_llm
from app.memory import memory

from app.security import (
    log_command_received,
    log_intent_detected,
    log_response_generated,
)


def process_command(command: str) -> str:
    log_command_received()

    result = detect_intent(command)

    intent = result["intent"]
    entities = result["entities"]

    log_intent_detected(intent, result["confidence"])

    # Greeting
    if intent == "greeting":
        response = (
            "Hello! I am your AI Chat Assistant. "
            "How can I help you?"
        )

    # Time
    elif intent == "get_time":
        response = datetime.now().strftime(
            "The current time is %I:%M %p."
        )

    # Date
    elif intent == "get_date":
        response = datetime.now().strftime(
            "Today's date is %d %B %Y."
        )

    # Assistant identity
    elif intent == "assistant_identity":
        response = "I am your AI Chat Assistant."

    # Open installed application
    elif intent == "open_application":
        response = execute_tool(
            "open_application",
            application=entities["application"]
        )

    # Google / Web search
    elif intent == "web_search":
        response = execute_tool(
            "web_search",
            query=entities["query"]
        )

    # YouTube search
    elif intent == "youtube_search":
        response = execute_tool(
            "youtube_search",
            query=entities["query"]
        )

    # Open YouTube
    elif intent == "open_youtube":
        response = execute_tool("open_youtube")

    # Calculator
    elif intent == "calculate":
        response = execute_tool(
            "calculate",
            expression=entities["expression"]
        )

    # AI fallback
    else:
        response = ask_llm(
            command,
            conversation=memory.get_messages()
        )

    # Security logging
    log_response_generated()

    # Save conversation
    memory.add_message("user", command)
    memory.add_message("assistant", response)

    return str(response)