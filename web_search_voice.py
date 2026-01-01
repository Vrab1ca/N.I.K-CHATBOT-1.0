# web_search_voice.py
# Human-like multi-step information search & synthesis

import wikipedia
from duckduckgo_search import DDGS
import re


# =========================
# TEXT UTILITIES
# =========================
def clean_text(text):
    text = re.sub(r"\[[0-9]+\]", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def split_sentences(text):
    return re.split(r"(?<=[.!?])\s+", text)


def deduplicate(sentences):
    seen = set()
    out = []
    for s in sentences:
        k = s.lower()
        if k not in seen and len(s) > 40:
            seen.add(k)
            out.append(s)
    return out


def score_sentence(sentence, keywords):
    score = 0
    s = sentence.lower()
    for k in keywords:
        if k in s:
            score += 2
    if any(x in s for x in ["century", "period", "empire", "independence", "founded"]):
        score += 1
    return score


# =========================
# WIKIPEDIA SEARCH
# =========================
def wiki_search(query, sentences=12):
    try:
        wikipedia.set_lang("en")
        return clean_text(wikipedia.summary(query, sentences=sentences))
    except Exception:
        return ""


# =========================
# WEB SEARCH (MULTI RESULT)
# =========================
def web_search(query, max_results=5):
    texts = []
    try:
        with DDGS() as ddgs:
            for r in ddgs.text(query, max_results=max_results):
                body = r.get("body", "")
                if body and len(body) > 80:
                    texts.append(clean_text(body))
    except Exception:
        pass
    return texts


# =========================
# QUERY GENERATOR (THINKING)
# =========================
def generate_queries(topic, intent):
    base = topic.lower()

    if intent == "history":
        return [
            f"history of {base}",
            f"{base} ancient medieval modern history",
            f"{base} historical timeline",
            f"{base} major historical events",
            f"{base} empire independence"
        ]

    return [
        base,
        f"{base} explanation",
        f"{base} overview",
        f"what is {base}"
    ]


# =========================
# MAIN SMART SEARCH
# =========================
def smart_search(topic, intent="general", mode="long"):
    collected = []

    # 1️⃣ Wikipedia first (trusted base)
    wiki = wiki_search(topic)
    if wiki:
        collected.append(wiki)

    # 2️⃣ Multi-query web search
    queries = generate_queries(topic, intent)
    for q in queries:
        collected.extend(web_search(q))

    # 3️⃣ Sentence processing
    sentences = []
    for block in collected:
        sentences.extend(split_sentences(block))

    sentences = deduplicate(sentences)

    if not sentences:
        return ""

    # 4️⃣ Ranking
    keywords = topic.lower().split()
    ranked = sorted(
        sentences,
        key=lambda s: score_sentence(s, keywords),
        reverse=True
    )

    # 5️⃣ Build response
    if mode == "short":
        return " ".join(ranked[:3])

    # Long structured response
    intro = ranked[0]

    ancient, medieval, modern = [], [], []

    for s in ranked:
        l = s.lower()
        if any(w in l for w in ["ancient", "roman", "thrac"]):
            ancient.append(s)
        elif any(w in l for w in ["medieval", "empire", "ottoman", "byzant"]):
            medieval.append(s)
        elif any(w in l for w in ["modern", "independ", "world war", "20th"]):
            modern.append(s)

    response = intro

    if ancient:
        response += "\n\nAncient period: " + " ".join(ancient[:3])
    if medieval:
        response += "\n\nMedieval period: " + " ".join(medieval[:3])
    if modern:
        response += "\n\nModern period: " + " ".join(modern[:3])

    return response.strip()
