import re
from typing import List

from app.domain.document_models import StoredChunk


STOP_WORDS = {
    "a", "an", "and", "are", "as", "at", "be", "but", "by", "for", "if", "in", 
    "into", "is", "it", "no", "not", "of", "on", "or", "such", "that", "the", 
    "their", "then", "there", "these", "they", "this", "to", "was", "will", "with"
}

def tokenize(text: str) -> set[str]:
    # Simple tokenization: lowercase, extract alphanumeric words
    tokens = re.findall(r'\b[a-z0-9]+\b', text.lower())
    return {t for t in tokens if t not in STOP_WORDS}


class RetrievalService:
    def retrieve_chunks(self, query: str, chunks: List[StoredChunk], top_k: int = 15) -> List[StoredChunk]:
        """
        MVP retrieval using simple keyword overlap tokenization.
        Later, this can be swapped with a vector search approach.
        """
        query_tokens = tokenize(query)
        if not query_tokens:
            # If query has no meaningful keywords, just return first few chunks or something.
            return chunks[:top_k]

        scored_chunks = []
        for chunk in chunks:
            chunk_tokens = tokenize(chunk.normalized_text)
            # Score is the number of query tokens present in the chunk
            overlap = len(query_tokens.intersection(chunk_tokens))
            
            # Boost score slightly if exact phrases match
            exact_match_boost = 0
            if query.lower() in chunk.normalized_text.lower():
                exact_match_boost += 5
                
            scored_chunks.append((overlap + exact_match_boost, chunk))
        
        # Sort by score descending
        scored_chunks.sort(key=lambda x: x[0], reverse=True)
        
        # Filter chunks that have at least some relevance, or just return top_k
        results = [c for score, c in scored_chunks if score > 0]
        
        if not results:
            return chunks[:top_k]
            
        return results[:top_k]
