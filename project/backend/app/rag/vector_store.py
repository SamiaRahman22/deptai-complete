"""
FAISS Vector Store.
Manages the FAISS index for semantic similarity search.
Supports persistent storage and incremental updates.
"""

import os
import json
import numpy as np
from typing import List, Tuple, Optional
from dataclasses import dataclass, asdict
from loguru import logger
from app.core.config import settings


@dataclass
class IndexedChunk:
    text: str
    source: str
    chunk_index: int
    doc_id: Optional[int] = None


class FAISSVectorStore:
    """
    FAISS-based vector store with metadata management.
    
    Stores:
    - FAISS index (binary) for fast similarity search
    - Chunk metadata (JSON) for text retrieval
    """

    def __init__(self, index_path: str = None):
        self.index_path = index_path or settings.FAISS_INDEX_PATH
        self.index_file = os.path.join(self.index_path, "index.faiss")
        self.meta_file = os.path.join(self.index_path, "metadata.json")
        
        self._index = None
        self._chunks: List[IndexedChunk] = []
        self._dimension: Optional[int] = None

    def _get_faiss(self):
        try:
            import faiss
            return faiss
        except ImportError:
            raise ImportError("faiss-cpu not installed. Run: pip install faiss-cpu")

    def initialize(self, dimension: int):
        """Initialize a new empty FAISS flat IP index."""
        faiss = self._get_faiss()
        self._dimension = dimension
        # Inner product index (works with L2-normalized embeddings for cosine similarity)
        self._index = faiss.IndexFlatIP(dimension)
        self._chunks = []
        logger.info(f"✅ FAISS index initialized (dim={dimension})")

    def add_embeddings(self, embeddings: np.ndarray, chunks: List[IndexedChunk]):
        """Add embeddings and their metadata to the index."""
        if self._index is None:
            raise RuntimeError("Index not initialized. Call initialize() first.")
        if len(embeddings) != len(chunks):
            raise ValueError("embeddings and chunks must have same length")

        embeddings = embeddings.astype(np.float32)
        self._index.add(embeddings)
        self._chunks.extend(chunks)
        logger.debug(f"Added {len(chunks)} chunks to FAISS index (total: {len(self._chunks)})")

    def search(self, query_embedding: np.ndarray, top_k: int = 5) -> List[Tuple[IndexedChunk, float]]:
        """
        Search for most similar chunks.
        Returns list of (chunk, score) tuples, sorted by descending score.
        """
        if self._index is None or self._index.ntotal == 0:
            return []

        query = query_embedding.astype(np.float32)
        if query.ndim == 1:
            query = query.reshape(1, -1)

        k = min(top_k, self._index.ntotal)
        scores, indices = self._index.search(query, k)

        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx >= 0 and idx < len(self._chunks) and score > 0.1:
                results.append((self._chunks[idx], float(score)))

        return results

    def save(self):
        """Persist index and metadata to disk."""
        if self._index is None:
            return
        faiss = self._get_faiss()
        os.makedirs(self.index_path, exist_ok=True)
        faiss.write_index(self._index, self.index_file)
        
        meta = {
            "dimension": self._dimension,
            "total_chunks": len(self._chunks),
            "chunks": [asdict(c) for c in self._chunks],
        }
        with open(self.meta_file, "w") as f:
            json.dump(meta, f, indent=2)
        
        logger.info(f"💾 FAISS index saved ({len(self._chunks)} chunks)")

    def load(self) -> bool:
        """Load index and metadata from disk. Returns True if successful."""
        if not os.path.exists(self.index_file) or not os.path.exists(self.meta_file):
            return False
        try:
            faiss = self._get_faiss()
            self._index = faiss.read_index(self.index_file)
            
            with open(self.meta_file) as f:
                meta = json.load(f)
            
            self._dimension = meta["dimension"]
            self._chunks = [IndexedChunk(**c) for c in meta["chunks"]]
            logger.info(f"✅ FAISS index loaded ({len(self._chunks)} chunks)")
            return True
        except Exception as e:
            logger.error(f"Failed to load FAISS index: {e}")
            return False

    def clear(self):
        """Reset the index."""
        if self._dimension:
            self.initialize(self._dimension)

    @property
    def total_chunks(self) -> int:
        return len(self._chunks)

    @property
    def is_ready(self) -> bool:
        return self._index is not None and self._index.ntotal > 0


vector_store = FAISSVectorStore()
