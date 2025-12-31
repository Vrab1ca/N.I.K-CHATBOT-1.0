import wikipediaapi
from ddgs import DDGS

wiki = wikipediaapi.Wikipedia(
    language="en",
    user_agent="NIKChatBot/1.0"
)

def wiki_search(query):
    page = wiki.page(query)
    if page.exists():
        text = page.summary
        if len(text.split()) > 80:
            return text
    return None

def web_search(query, max_results=2):
    results = []
    with DDGS() as ddgs:
        for r in ddgs.text(query, max_results=max_results):
            title = r.get("title", "")
            body = r.get("body", "")
            if len(body.split()) > 40:
                results.append(f"{title}: {body}")
    return " ".join(results) if results else None
