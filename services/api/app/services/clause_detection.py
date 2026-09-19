import re
from dataclasses import dataclass

from app.domain.document_models import StoredClause, StoredPage


PAGE_SEPARATOR = "\n\n"


@dataclass(frozen=True)
class LineRecord:
    text: str
    start_offset: int
    end_offset: int
    page_number: int


@dataclass(frozen=True)
class ClauseStart:
    clause_number: str | None
    title: str | None
    start_offset: int
    page_number: int


DECIMAL_PATTERN = re.compile(r"^\s*((?:\d{1,3}\.)+\d{1,3})(?:[.)])?\s+(.+?)\s*$")
NUMBERED_PATTERN = re.compile(r"^\s*(\d{1,3})(?:[.)])\s+(.+?)\s*$")
NUMBERED_SPACE_PATTERN = re.compile(r"^\s*(\d{1,3})\s+([A-Z][^\n]{2,})\s*$")
NUMBER_ONLY_PATTERN = re.compile(r"^\s*(\d{1,3})(?:[.)])?\s*$")
PAREN_PATTERN = re.compile(r"^\s*(\([a-z]\))\s+(.+?)\s*$")


def build_corpus(pages: list[StoredPage]) -> str:
    return PAGE_SEPARATOR.join(page.raw_text for page in pages)


def build_line_records(pages: list[StoredPage]) -> list[LineRecord]:
    records: list[LineRecord] = []

    for page in pages:
        offset = page.start_offset
        for line in page.raw_text.splitlines(keepends=True):
            line_start = offset
            line_end = offset + len(line)
            offset = line_end

            visible = line.rstrip("\r\n")
            if visible.strip():
                records.append(
                    LineRecord(
                        text=visible,
                        start_offset=line_start,
                        end_offset=line_end,
                        page_number=page.page_number,
                    )
                )

    return records


def detect_clauses(pages: list[StoredPage]) -> list[StoredClause]:
    corpus = build_corpus(pages)
    lines = build_line_records(pages)
    numbered_starts = _detect_numbered_starts(lines)
    starts = numbered_starts if numbered_starts else _detect_unnumbered_heading_starts(lines)

    clauses: list[StoredClause] = []
    for index, start in enumerate(starts):
        next_start = starts[index + 1].start_offset if index + 1 < len(starts) else len(corpus)
        source_text = corpus[start.start_offset:next_start].rstrip()
        if not source_text.strip():
            continue

        end_offset = start.start_offset + len(source_text)
        page_start, page_end = page_range_for_offsets(pages, start.start_offset, end_offset)
        clauses.append(
            StoredClause(
                clause_id=f"clause_{len(clauses) + 1}",
                clause_number=start.clause_number,
                title=start.title,
                page_start=page_start,
                page_end=page_end,
                source_text=source_text,
                start_offset=start.start_offset,
                end_offset=end_offset,
            )
        )

    return clauses


def page_range_for_offsets(pages: list[StoredPage], start_offset: int, end_offset: int) -> tuple[int, int]:
    matched = [
        page.page_number
        for page in pages
        if page.end_offset > start_offset and page.start_offset < end_offset
    ]
    if matched:
        return min(matched), max(matched)

    nearest = min(pages, key=lambda page: abs(page.start_offset - start_offset))
    return nearest.page_number, nearest.page_number


def _detect_numbered_starts(lines: list[LineRecord]) -> list[ClauseStart]:
    starts: list[ClauseStart] = []

    for index, line in enumerate(lines):
        match = _match_numbered_clause(line.text)
        if match is None:
            continue

        clause_number, title = match
        if title is None and index + 1 < len(lines):
            next_line = lines[index + 1].text.strip()
            title = next_line if is_heading_like(next_line) else None

        starts.append(
            ClauseStart(
                clause_number=clause_number,
                title=title,
                start_offset=line.start_offset,
                page_number=line.page_number,
            )
        )

    return starts


def _detect_unnumbered_heading_starts(lines: list[LineRecord]) -> list[ClauseStart]:
    starts: list[ClauseStart] = []

    for index, line in enumerate(lines[:-1]):
        text = line.text.strip()
        next_text = lines[index + 1].text.strip()
        if is_heading_like(text) and next_text and not is_heading_like(next_text):
            starts.append(
                ClauseStart(
                    clause_number=None,
                    title=text,
                    start_offset=line.start_offset,
                    page_number=line.page_number,
                )
            )

    return starts


def _match_numbered_clause(text: str) -> tuple[str, str | None] | None:
    for pattern in (DECIMAL_PATTERN, NUMBERED_PATTERN, PAREN_PATTERN):
        match = pattern.match(text)
        if match:
            return match.group(1), match.group(2).strip()

    match = NUMBERED_SPACE_PATTERN.match(text)
    if match:
        return match.group(1), match.group(2).strip()

    match = NUMBER_ONLY_PATTERN.match(text)
    if match:
        return match.group(1), None

    return None


def is_heading_like(text: str) -> bool:
    stripped = text.strip()
    if not stripped or len(stripped) > 80 or stripped.endswith((".", ";", ",")):
        return False

    words = [word for word in re.split(r"\s+", stripped) if word]
    if not 1 <= len(words) <= 8:
        return False

    if any(char.isdigit() for char in stripped):
        return False

    scored_words = [word.strip(":()[]") for word in words]
    capitalized = [
        word
        for word in scored_words
        if word.isupper() or (word[:1].isupper() and not word.islower())
    ]
    return len(capitalized) / len(scored_words) >= 0.6

