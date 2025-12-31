# web_search_voice.py
# Internet search for voice bot (FAST & SIMPLE)

import wikipedia
from duckduckgo_search import DDGS


# =========================
# WIKIPEDIA SEARCH
# =========================
def search_wikipedia(query):
    try:
        wikipedia.set_lang("en")
        return wikipedia.summary(query, sentences=2)
    except wikipedia.exceptions.DisambiguationError:
        return "That topic has multiple meanings. Please be more specific."
    except wikipedia.exceptions.PageError:
        return ""
    except Exception:
        return ""


# =========================
# WEB SEARCH (DuckDuckGo)
# =========================
def search_web(query):
    try:
        with DDGS() as ddgs:
            results = ddgs.text(query, max_results=2)
            for r in results:
                return r["body"]
    except Exception:
        pass
    return ""
