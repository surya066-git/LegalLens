import re

from app.domain.document_models import StoredChunk, StoredClause, StoredPage
from app.services.clause_detection import build_corpus, page_range_for_offsets
from app.services.text_normalization import normalize_search_text


PARAGRAPH_PATTERN = re.compile(r"\S[\s\S]*?(?=\n\s*\n|\Z)")


def chunk_document(pages: list[StoredPage], clauses: list[StoredClause]) -> list[StoredChunk]:
    if clauses:
        return _chunk_with_clauses(pages, clauses)
    return _chunk_by_page_paragraphs(pages)


def _chunk_with_clauses(pages: list[StoredPage], clauses: list[StoredClause]) -> list[StoredChunk]:
    chunks: list[StoredChunk] = []
    corpus = build_corpus(pages)
    first_clause_start = clauses[0].start_offset

    if first_clause_start > 0:
        chunks.extend(
            _paragraph_chunks_from_text(
                pages=pages,
                text=corpus[:first_clause_start],
                base_offset=0,
                chunk_prefix="chunk",
                starting_index=1,
            )
        )

    for clause in clauses:
        if len(clause.source_text) <= 2800:
            chunks.append(
                StoredChunk(
                    chunk_id=f"chunk_{len(chunks) + 1}",
                    clause_id=clause.clause_id,
                    clause_number=clause.clause_number,
                    page_start=clause.page_start,
                    page_end=clause.page_end,
                    source_text=clause.source_text,
                    normalized_text=normalize_search_text(clause.source_text),
                    start_offset=clause.start_offset,
                    end_offset=clause.end_offset,
                )
            )
            continue

        chunks.extend(
            _paragraph_chunks_from_text(
                pages=pages,
                text=clause.source_text,
                base_offset=clause.start_offset,
                chunk_prefix="chunk",
                starting_index=len(chunks) + 1,
                clause_id=clause.clause_id,
                clause_number=clause.clause_number,
            )
        )

    return chunks


def _chunk_by_page_paragraphs(pages: list[StoredPage]) -> list[StoredChunk]:
    chunks: list[StoredChunk] = []
    for page in pages:
        chunks.extend(
            _paragraph_chunks_from_text(
                pages=pages,
                text=page.raw_text,
                base_offset=page.start_offset,
                chunk_prefix="chunk",
                starting_index=len(chunks) + 1,
            )
        )
    return chunks


def _paragraph_chunks_from_text(
    pages: list[StoredPage],
    text: str,
    base_offset: int,
    chunk_prefix: str,
    starting_index: int,
    clause_id: str | None = None,
    clause_number: str | None = None,
) -> list[StoredChunk]:
    chunks: list[StoredChunk] = []
    for match in PARAGRAPH_PATTERN.finditer(text):
        source_text = match.group(0).strip()
        if not source_text:
            continue

        leading_trim = len(match.group(0)) - len(match.group(0).lstrip())
        start_offset = base_offset + match.start() + leading_trim
        end_offset = start_offset + len(source_text)
        page_start, page_end = page_range_for_offsets(pages, start_offset, end_offset)
        chunks.append(
            StoredChunk(
                chunk_id=f"{chunk_prefix}_{starting_index + len(chunks)}",
                clause_id=clause_id,
                clause_number=clause_number,
                page_start=page_start,
                page_end=page_end,
                source_text=source_text,
                normalized_text=normalize_search_text(source_text),
                start_offset=start_offset,
                end_offset=end_offset,
            )
        )
    return chunks

