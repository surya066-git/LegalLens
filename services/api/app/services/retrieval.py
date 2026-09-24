from __future__ import annotations

import re
from typing import List

from app.domain.document_models import StoredChunk


STOP_WORDS = {
    "a", "an", "and", "are", "as", "at", "be", "but", "by", "for", "if", "in",
    "into", "is", "it", "no", "not", "of", "on", "or", "such", "that", "the",
    "their", "then", "there", "these", "they", "this", "to", "was", "will", "with",
    "what", "does", "do", "can", "could", "please", "tell", "me", "about", "which",
}

SYNONYMS = {
    "salary": ["compensation", "remuneration", "pay", "wages"],
    "compensation": ["salary", "remuneration", "pay", "wages"],
    "remuneration": ["salary", "compensation", "pay"],
    "pay": ["salary", "compensation", "remuneration", "wages"],
    "wages": ["salary", "pay", "compensation"],
    "termination": ["dismissal", "ending", "terminate"],
    "dismissal": ["termination", "terminate"],
    "terminate": ["termination", "dismissal"],
    "notice": ["notification"],
    "probation": ["probationary"],
    "probationary": ["probation"],
    "leave": ["vacation", "absence", "holiday"],
    "vacation": ["leave", "absence", "holiday"],
    "confidentiality": ["confidential", "non-disclosure", "nda"],
    "confidential": ["confidentiality"],
    "restriction": ["non-compete", "covenant", "noncompete"],
    "hours": ["working"],
    "start": ["joining", "commencement", "commence"],
    "joining": ["start", "commencement"],
}

PHRASES = (
    "notice period",
    "non-compete",
    "non compete",
    "garden leave",
    "severance pay",
    "probation period",
    "working hours",
    "intellectual property",
)


def tokenize(text: str) -> set[str]:
    tokens = set(re.findall(r"[a-z0-9]+(?:-[a-z0-9]+)?", text.lower()))
    return tokens - STOP_WORDS


def expand_tokens(tokens: set[str]) -> set[str]:
    expanded = set(tokens)
    for token in tokens:
        if token in SYNONYMS:
            expanded.update(SYNONYMS[token])
    return expanded


class RetrievalService:
    def retrieve_chunks(self, query: str, chunks: List[StoredChunk], top_k: int = 15) -> List[StoredChunk]:
        if not chunks:
            return []

        query_lower = query.lower()
        query_tokens = expand_tokens(tokenize(query))
        clause_match = re.search(r"\b(?:clause|section|article)\s+(\d+(?:\.\d+)*)", query_lower)
        page_match = re.search(r"\bpage\s+(\d+)", query_lower)
        wanted_clause = clause_match.group(1) if clause_match else None
        wanted_page = int(page_match.group(1)) if page_match else None

        scored: list[tuple[float, StoredChunk]] = []
        for chunk in chunks:
            text = chunk.normalized_text.lower()
            chunk_tokens = tokenize(chunk.normalized_text)
            overlap = len(query_tokens.intersection(chunk_tokens))
            score = float(overlap)

            if query_lower in text:
                score += 6
            for phrase in PHRASES:
                if phrase in query_lower and phrase in text:
                    score += 4

            if wanted_clause and chunk.clause_number:
                if chunk.clause_number == wanted_clause or chunk.clause_number.startswith(wanted_clause + "."):
                    score += 8

            if wanted_page is not None and chunk.page_start <= wanted_page <= chunk.page_end:
                score += 3

            if score > 0:
                scored.append((score, chunk))

        scored.sort(key=lambda item: item[0], reverse=True)
        seen: set[str] = set()
        results: list[StoredChunk] = []
        for _, chunk in scored:
            if chunk.chunk_id in seen:
                continue
            seen.add(chunk.chunk_id)
            results.append(chunk)
            if len(results) >= top_k:
                break
        return results
