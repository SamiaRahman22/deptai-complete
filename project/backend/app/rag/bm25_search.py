"""
BM25 Keyword Search Module.
Provides fast keyword-based retrieval using Okapi BM25 algorithm.
"""

from typing import List, Tuple, Dict
from loguru import logger

# Need to install: pip install rank-bm25


class BM25Searcher:
    """
    BM25-based keyword search for quick term matching.
    """

    def __init__(self):
        self._corpus = []  # List of chunk texts
        self._bm25 = None
        self._chunk_metadata = []

    def build_index(self, chunks: List[Dict]) -> None:
        """
        Build BM25 index from chunks.
        
        chunks format: [
            {"text": "...", "source": "...", "index": 0},
            ...
        ]
        """
        from rank_bm25 import BM25Okapi
        
        # Tokenize all chunks
        tokenized_corpus = []
        self._corpus = []
        self._chunk_metadata = []
        
        for chunk in chunks:
            text = chunk.get("text", "")
            # Simple tokenization: lowercase, split on whitespace
            tokens = text.lower().split()
            tokenized_corpus.append(tokens)
            
            self._corpus.append(text)
            self._chunk_metadata.append({
                "source": chunk.get("source", "unknown"),
                "index": chunk.get("index", 0),
            })
        
        if not tokenized_corpus:
            logger.warning("No chunks to index for BM25")
            return
        
        self._bm25 = BM25Okapi(tokenized_corpus)
        logger.info(f"BM25 index built from {len(chunks)} chunks")

    def search(self, query: str, top_k: int = 10) -> List[Tuple[str, float, Dict]]:
        """
        Search using BM25 algorithm.
        
        Returns:
            List of (chunk_text, score, metadata) tuples
        """
        if self._bm25 is None:
            return []
        
        # Tokenize query
        tokens = query.lower().split()
        
        # Get BM25 scores
        scores = self._bm25.get_scores(tokens)
        
        # Get top-k indices
        top_indices = sorted(
            range(len(scores)),
            key=lambda i: scores[i],
            reverse=True
        )[:top_k]
        
        results = []
        for idx in top_indices:
            if scores[idx] > 0:  # Only include if score > 0
                results.append((
                    self._corpus[idx],
                    float(scores[idx]),
                    self._chunk_metadata[idx]
                ))
        
        logger.debug(f"BM25 search returned {len(results)} results")
        return results

    def is_ready(self) -> bool:
        """Check if index is ready."""
        return self._bm25 is not None


bm25_searcher = BM25Searcher()