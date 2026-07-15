import os
import requests
from dotenv import load_dotenv
from langchain_core.tools import tool

load_dotenv()

BRAVE_API_KEY = os.getenv("BRAVE_API_KEY")
BRAVE_ENDPOINT = "https://api.search.brave.com/res/v1/web/search"


@tool
def Search(query: str) -> str:
    """Search the web for up-to-date information using Brave Search.

    Returns a plain-text digest of the top results (title, url, snippet).
    """
    if not BRAVE_API_KEY:
        return "Brave Search API key is not configured."

    headers = {
        "X-Subscription-Token": BRAVE_API_KEY,
        "Accept": "application/json",
    }
    params = {"q": query, "count": 5}

    try:
        resp = requests.get(BRAVE_ENDPOINT, headers=headers, params=params, timeout=15)
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        return f"Brave Search request failed: {e}"

    results = data.get("web", {}).get("results", [])
    if not results:
        return "No results found."

    lines = []
    for r in results[:5]:
        title = r.get("title", "")
        url = r.get("url", "")
        desc = r.get("description", "")
        lines.append(f"{title}\n{url}\n{desc}")

    return "\n\n".join(lines)
