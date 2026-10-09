import re


def detect_intent(text: str):
    text = text.lower().strip()
    text = re.sub(r"[.!?,]+", " ", text)
    text = " ".join(text.split())

    # -------------------------
    # Open YouTube
    # -------------------------
    if re.search(
        r"\b(open|launch|start|go to)\s+youtube\b",
        text
    ):
        return {
            "intent": "open_youtube",
            "confidence": 0.98,
            "entities": {}
        }

    # -------------------------
    # YouTube search
    # -------------------------
    patterns = [
        r"\bsearch\s+youtube\s+(?:for\s+)?(.+)$",
        r"\bfind\s+(.+?)\s+on\s+youtube\b",
        r"\bplay\s+(.+?)\s+on\s+youtube\b",
        r"\bplay\s+(.+)$",
    ]

    for pattern in patterns:
        match = re.search(pattern, text)

        if match:
            query = match.group(1).strip()

            if query:
                return {
                    "intent": "youtube_search",
                    "confidence": 0.94,
                    "entities": {
                        "query": query
                    }
                }

    # -------------------------
    # Open installed application
    # -------------------------
    match = re.search(
        r"\b(?:open|launch|start|run)\s+(.+)$",
        text
    )

    if match:
        application = match.group(1).strip()

        # Remove a greeting from the beginning.
        application = re.sub(
            r"^(hi|hello|hey|hii|namaste)\s+",
            "",
            application
        ).strip()

        if application:
            return {
                "intent": "open_application",
                "confidence": 0.90,
                "entities": {
                    "application": application
                }
            }

    # -------------------------
    # Web search
    # -------------------------
    match = re.search(
        r"\b(?:search|google)\s+(?:the web\s+)?(?:for\s+)?(.+)$",
        text
    )

    if match:
        query = match.group(1).strip()

        if query:
            return {
                "intent": "web_search",
                "confidence": 0.90,
                "entities": {
                    "query": query
                }
            }

    # -------------------------
    # Time
    # -------------------------
    if re.search(
        r"\b(what time|current time|tell me the time)\b",
        text
    ) or text == "time":
        return {
            "intent": "get_time",
            "confidence": 0.95,
            "entities": {}
        }

    # -------------------------
    # Date
    # -------------------------
    if re.search(
        r"\b(today's date|current date|what is the date|what's the date)\b",
        text
    ) or text == "date":
        return {
            "intent": "get_date",
            "confidence": 0.95,
            "entities": {}
        }

    # -------------------------
    # Assistant identity
    # -------------------------
    if (
        "your name" in text
        or "who are you" in text
        or "what are you" in text
    ):
        return {
            "intent": "assistant_identity",
            "confidence": 0.95,
            "entities": {}
        }

    # -------------------------
    # Calculator
    # -------------------------
    match = re.search(
        r"\b(?:calculate|solve|what is)\s+(.+)$",
        text
    )

    if match:
        expression = match.group(1).strip()

        if re.search(r"\d", expression) and re.search(
            r"[+\-*/%()]",
            expression
        ):
            return {
                "intent": "calculate",
                "confidence": 0.90,
                "entities": {
                    "expression": expression
                }
            }

    # -------------------------
    # Greeting
    # -------------------------
    if re.fullmatch(
        r"(hi|hello|hey|hii|namaste|good morning|good afternoon|good evening)",
        text
    ):
        return {
            "intent": "greeting",
            "confidence": 0.98,
            "entities": {}
        }

    # -------------------------
    # Generic song/music request
    # -------------------------
    if re.search(
        r"\b(search|find|play|look for)\b.*\b(song|music)\b",
        text
    ):
        query = re.sub(
            r"\b(search|find|play|look for|song|music)\b",
            "",
            text
        ).strip()

        if query:
            return {
                "intent": "youtube_search",
                "confidence": 0.94,
                "entities": {
                    "query": query
                }
            }

        return {
            "intent": "open_youtube",
            "confidence": 0.90,
            "entities": {}
        }

    # -------------------------
    # Unknown: send to AI model
    # -------------------------
    return {
        "intent": "unknown",
        "confidence": 0.30,
        "entities": {}
    }