# web_search_voice.py
# Stable, ChatGPT-like factual search & synthesis (VOICE SAFE)

import wikipedia
from duckduckgo_search import DDGS
import re
from urllib.parse import urlparse


# =========================
# TRUSTED SOURCES (PRIORITY)
# =========================
TRUSTED_DOMAINS = [
    "wikipedia.org",
    "britannica.com",
    "bbc.com",
    "nationalgeographic.com",
    "nasa.gov",
    "smithsonianmag.com",
    "https://www.gov.bg"
]


# =========================
# TEXT UTILITIES
# =========================
def clean_text(text: str) -> str:
    text = re.sub(r"\[[0-9]+\]", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def split_sentences(text: str):
    return re.split(r"(?<=[.!?])\s+", text)


def deduplicate(sentences):
    seen = set()
    out = []
    for s in sentences:
        key = s.lower()
        if key not in seen and len(s) > 50:
            seen.add(key)
            out.append(s)
    return out


def score_sentence(sentence, keywords):
    s = sentence.lower()
    score = 0

    for k in keywords:
        if k in s:
            score += 2

    if any(w in s for w in ["century", "period", "empire", "independence", "founded"]):
        score += 1

    return score


# =========================
# WIKIPEDIA BASE
# =========================
def wiki_search(query, sentences=8):
    try:
        wikipedia.set_lang("en")
        return clean_text(wikipedia.summary(query, sentences=sentences))
    except Exception:
        return ""


# =========================
# WEB SEARCH (SAFE MODE)
# =========================
def web_search(query, max_results=6):
    results = []

    try:
        with DDGS() as ddgs:
            for r in ddgs.text(query, max_results=max_results):
                body = clean_text(r.get("body", ""))
                url = r.get("href", "")
                title = r.get("title", "") or url

                if len(body) < 80:
                    continue

                results.append({
                    "title": title,
                    "text": body,
                    "url": url,
                    "domain": urlparse(url).netloc
                })
    except Exception:
        pass

    # prioritize trusted domains
    results.sort(
        key=lambda r: any(d in r["domain"] for d in TRUSTED_DOMAINS),
        reverse=True
    )

    return results


# =========================
# QUERY GENERATION (THINKING)
# =========================
def generate_queries(topic, intent):
    t = topic.lower()

    if intent == "history":
        return [
            f"history of {t}",
            f"{t} ancient history",
            f"{t} medieval history",
            f"{t} modern history",
            f"{t} major historical events",
        ]

    return [
        f"{t}",
        f"{t} explanation",
        f"{t} overview",
        f"what is {t}",
    ]


# =========================
# MAIN SEARCH (CHATGPT-LIKE)
# =========================
def smart_search(topic, intent="general", mode="long"):
    sources = []

    # 1️⃣ Wikipedia (trusted backbone)
    wiki = wiki_search(topic)
    if wiki:
        sources.append({
            "title": f"Wikipedia – {topic}",
            "text": wiki,
            "url": f"https://en.wikipedia.org/wiki/{topic.replace(' ', '_')}",
            "domain": "wikipedia.org"
        })

    # 2️⃣ Multi-query web search
    for q in generate_queries(topic, intent):
        for hit in web_search(q):
            if not any(hit["url"] == s["url"] for s in sources):
                sources.append(hit)

    if not sources:
        return "I could not find reliable information."

    # 3️⃣ Sentence aggregation
    sentences = []
    for s in sources:
        sentences.extend(split_sentences(s["text"]))

    sentences = deduplicate(sentences)
    if not sentences:
        return "No clear information extracted."

    # 4️⃣ Ranking
    keywords = [k for k in topic.lower().split() if len(k) > 2]
    ranked = sorted(
        sentences,
        key=lambda s: score_sentence(s, keywords),
        reverse=True
    )

    # SHORT MODE (VOICE FAST)
    if mode == "short":
        return " ".join(ranked[:3])

    # 5️⃣ Structured response
    overview = ranked[0]
    facts = ranked[1:7]

    response = []
    response.append(f"Topic: {topic}")
    response.append("")
    response.append("Overview:")
    response.append(overview)
    response.append("")
    response.append("Key points:")

    for f in facts:
        response.append("- " + f)

    response.append("")
    response.append("Sources:")
    for i, s in enumerate(sources[:5], start=1):
        response.append(f"{i}. {s['domain']}")

    return "\n".join(response).strip()
