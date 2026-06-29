"""
Enhanced Text Chunking Module.
Splits documents into overlapping chunks while preserving semantic boundaries.
Now uses token-based sizing (better than word-based).
"""

import re
from typing import List
from dataclasses import dataclass
from app.core.config import settings


@dataclass
class TextChunk:
    text: str
    index: int
    source: str
    char_start: int
    char_end: int


def _estimate_tokens(text: str) -> int:
    """
    Rough estimate of token count (for use without tokenizer).
    Estimates: ~1 token per 4 characters on average.
    """
    return len(text) // 4 + 1


def chunk_text(
    text: str,
    source: str,
    chunk_size: int = None,
    chunk_overlap: int = None,
) -> List[TextChunk]:
    """
    Split text into overlapping chunks using adaptive strategy.
    
    Strategy:
    1. Split into sentences (preserves semantic boundaries)
    2. Group sentences into chunks by token count
    3. Overlap chunks to preserve context
    4. Filter short/long outliers
    """
    chunk_size = chunk_size or settings.CHUNK_SIZE  # Default 512 tokens
    chunk_overlap = chunk_overlap or settings.CHUNK_OVERLAP  # Default 50 tokens

    sentences = _split_sentences(text)
    if not sentences:
        return []

    chunks = []
    current_sentences = []
    current_tokens = 0
    current_start = 0
    chunk_idx = 0

    for sentence in sentences:
        sentence_tokens = _estimate_tokens(sentence)

        # If adding this sentence would exceed chunk_size, save current chunk
        if current_tokens + sentence_tokens > chunk_size and current_sentences:
            # Build chunk from sentences
            chunk_text_str = " ".join(current_sentences)
            chunks.append(TextChunk(
                text=chunk_text_str,
                index=chunk_idx,
                source=source,
                char_start=current_start,
                char_end=current_start + len(chunk_text_str),
            ))
            chunk_idx += 1

            # Start new chunk with overlap (last few sentences)
            overlap_count = 0
            overlap_tokens = 0
            for prev_sent in reversed(current_sentences):
                prev_tokens = _estimate_tokens(prev_sent)
                if overlap_tokens + prev_tokens <= chunk_overlap:
                    overlap_count += 1
                    overlap_tokens += prev_tokens
                else:
                    break

            current_sentences = current_sentences[-overlap_count:] if overlap_count > 0 else []
            current_tokens = overlap_tokens
            current_start += len(" ".join(current_sentences[:-1])) + 1 if len(current_sentences) > 1 else 0

        # Add sentence to current chunk
        current_sentences.append(sentence)
        current_tokens += sentence_tokens

    # Don't forget the last chunk
    if current_sentences:
        chunk_text_str = " ".join(current_sentences)
        chunks.append(TextChunk(
            text=chunk_text_str,
            index=chunk_idx,
            source=source,
            char_start=current_start,
            char_end=current_start + len(chunk_text_str),
        ))

    # Filter trivial chunks (too short)
    filtered_chunks = [c for c in chunks if len(c.text.strip()) > 50]

    if len(filtered_chunks) < len(chunks):
        removed = len(chunks) - len(filtered_chunks)
        # Merge small chunks with adjacent chunks
        # (Implementation: left as simple filtering for now)

    return filtered_chunks


def _split_sentences(text: str) -> List[str]:
    """
    Split text into sentences with paragraph awareness.
    Handles common edge cases.
    """
    # Remove extra whitespace and normalize
    text = re.sub(r'\n{3,}', '\n\n', text)  # Normalize paragraph breaks
    text = re.sub(r' {2,}', ' ', text)  # Normalize spaces

    # Split on paragraph breaks first
    paragraphs = re.split(r'\n\n+', text)
    sentences = []

    for para in paragraphs:
        para = para.strip()
        if not para:
            continue

        # Split paragraph into sentences
        # Handle common abbreviations that end with periods
        para = re.sub(r'\b(Dr|Mr|Mrs|Ms|Prof|Sr|Jr)\.', r'\1<ABBREV>', para)
        
        # Split on sentence boundaries (period, !, ?)
        para_sentences = re.split(r'(?<=[.!?])\s+(?=[A-Z0-9])', para)

        # Restore abbreviations
        para_sentences = [s.replace('<ABBREV>', '.') for s in para_sentences]
        
        sentences.extend(s.strip() for s in para_sentences if s.strip())

    # Filter very short sentences
    sentences = [s for s in sentences if len(s.split()) >= 3]

    return sentences