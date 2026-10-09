import webbrowser
from urllib.parse import quote_plus


def open_url(url: str) -> str:
    """Open a URL in the default browser."""
    try:
        webbrowser.open(url)
        return f"Opening {url}"
    except Exception:
        return "I couldn't open the requested website."


def search_web(query: str) -> str:
    """Search the web using Google."""
    query = query.strip()

    if not query:
        return "Please tell me what you want to search for."

    url = (
        "https://www.google.com/search?q="
        + quote_plus(query)
    )

    try:
        webbrowser.open(url)
        return f"Searching the web for: {query}"
    except Exception:
        return "I couldn't open the web search."


def search_youtube(query: str) -> str:
    """Search YouTube for a song, video, game, etc."""
    query = query.strip()

    if not query:
        return "Please tell me what you want to search on YouTube."

    url = (
        "https://www.youtube.com/results?search_query="
        + quote_plus(query)
    )

    try:
        webbrowser.open(url)
        return f"Searching YouTube for: {query}"
    except Exception:
        return "I couldn't open YouTube search."


def open_youtube() -> str:
    """Open YouTube."""
    try:
        webbrowser.open("https://www.youtube.com")
        return "Opening YouTube."
    except Exception:
        return "I couldn't open YouTube."