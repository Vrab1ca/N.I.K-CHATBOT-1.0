from ddgs import DDGS

TRUSTED_HINTS = [
    "wikipedia.org",
    "britannica.com",
    "bbc.com",
    "nasa.gov",
    "nationalgeographic.com"
]

def web_search(query, max_results=4):
    results = []
    with DDGS() as ddgs:
        for r in ddgs.text(query, max_results=max_results):
            title = r.get("title", "")
            body = r.get("body", "")
            url = r.get("href", "")

            if len(body.split()) < 40:
                continue

            # prefer educational / trusted sites
            if any(hint in url for hint in TRUSTED_HINTS) or not TRUSTED_HINTS:
                results.append({
                    "title": title,
                    "body": body,
                    "url": url
                })

    return results
