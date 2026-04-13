"""
Text Chunking Module.
Splits documents into overlapping chunks for embedding.
Uses sentence-aware splitting to avoid cutting mid-sentence.
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


def chunk_text(
    text: str,
    source: str,
    chunk_size: int = None,
    chunk_overlap: int = None,
) -> List[TextChunk]:
    """
    Split text into overlapping chunks.
    
    Strategy:
    1. Split into sentences
    2. Greedily fill chunks up to chunk_size tokens
    3. Overlap by chunk_overlap tokens between consecutive chunks
    """
    chunk_size = chunk_size or settings.CHUNK_SIZE
    chunk_overlap = chunk_overlap or settings.CHUNK_OVERLAP

    # Split into sentences
    sentences = _split_sentences(text)
    if not sentences:
        return []

    chunks = []
    current_words = []
    current_start = 0
    char_pos = 0
    chunk_idx = 0

    for sentence in sentences:
        sentence_words = sentence.split()
        
        if len(current_words) + len(sentence_words) > chunk_size and current_words:
            # Save current chunk
            chunk_text_str = " ".join(current_words)
            chunks.append(TextChunk(
                text=chunk_text_str,
                index=chunk_idx,
                source=source,
                char_start=current_start,
                char_end=current_start + len(chunk_text_str),
            ))
            chunk_idx += 1

            # Start next chunk with overlap
            overlap_words = current_words[-chunk_overlap:] if chunk_overlap else []
            current_words = overlap_words + sentence_words
            current_start = char_pos
        else:
            current_words.extend(sentence_words)

        char_pos += len(sentence) + 1

    # Don't forget the last chunk
    if current_words:
        chunk_text_str = " ".join(current_words)
        chunks.append(TextChunk(
            text=chunk_text_str,
            index=chunk_idx,
            source=source,
            char_start=current_start,
            char_end=current_start + len(chunk_text_str),
        ))

    return [c for c in chunks if len(c.text.strip()) > 50]  # Filter trivial chunks


def _split_sentences(text: str) -> List[str]:
    """Split text into sentences with paragraph awareness."""
    # Split on paragraph breaks first
    paragraphs = re.split(r"\n{2,}", text)
    sentences = []
    
    for para in paragraphs:
        para = para.strip()
        if not para:
            continue
        # Split paragraph into sentences
        para_sentences = re.split(r"(?<=[.!?])\s+(?=[A-Z])", para)
        sentences.extend(s.strip() for s in para_sentences if s.strip())

    return sentences
