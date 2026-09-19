import re
from typing import List

from app.domain.document_models import StoredChunk


STOP_WORDS = {
    "a", "an", "and", "are", "as", "at", "be", "but", "by", "for", "if", "in", 
    "into", "is", "it", "no", "not", "of", "on", "or", "such", "that", "the", 
    "their", "then", "there", "these", "they", "this", "to", "was", "will", "with",
    "what", "does", "do", "can", "could", "please", "tell", "me"
}

SYNONYMS = {
    "salary": ["compensation", "remuneration", "pay"],
    "compensation": ["salary", "remuneration", "pay"],
    "remuneration": ["salary", "compensation", "pay"],
    "pay": ["salary", "compensation", "remuneration"],
    
    "termination": ["dismissal", "ending"],
    "dismissal": ["termination"],
    
    "notice": ["notice period"],
    
    "probation": ["probationary"],
    "probationary": ["probation"],
    
    "leave": ["vacation", "absence"],
    "vacation": ["leave", "absence"],
    
    "confidentiality": ["confidential"],
    "confidential": ["confidentiality"],
    
    "non-compete": ["restrictive", "covenant", "post-employment", "restriction"],
    "restriction": ["non-compete", "covenant", "post-employment"],
    
    "hours": ["working"],
    
    "start": ["joining", "commencement", "date"]
}

def tokenize(text: str) -> set[str]:
    # Simple tokenization: lowercase, extract alphanumeric words
    tokens = set(re.findall(r'\b[a-z0-9]+\b', text.lower()))
    return tokens - STOP_WORDS

def expand_tokens(tokens: set[str]) -> set[str]:
    expanded = set(tokens)
    for t in tokens:
        if t in SYNONYMS:
            expanded.update(SYNONYMS[t])
    return expanded

class RetrievalService:
    def retrieve_chunks(self, query: str, chunks: List[StoredChunk], top_k: int = 15) -> List[StoredChunk]:
        query_tokens = tokenize(query)
        query_tokens = expand_tokens(query_tokens)
        
        if not query_tokens:
            return chunks[:top_k]

        scored_chunks = []
        for chunk in chunks:
            chunk_tokens = tokenize(chunk.normalized_text)
            overlap = len(query_tokens.intersection(chunk_tokens))
            
            exact_match_boost = 0
            if query.lower() in chunk.normalized_text.lower():
                exact_match_boost += 5
                
            scored_chunks.append((overlap + exact_match_boost, chunk))
        
        scored_chunks.sort(key=lambda x: x[0], reverse=True)
        results = [c for score, c in scored_chunks if score > 0]
        
        if not results:
            return []
            
        return results[:top_k]
