"""
Embedding Service using SentenceTransformers.
Generates dense vector embeddings for semantic search.
"""

import numpy as np
from typing import List, Optional
from loguru import logger
from app.core.config import settings


class EmbeddingService:
    """Wrapper around SentenceTransformers for generating embeddings."""

    def __init__(self):
        self._model = None
        self._model_name = settings.EMBEDDING_MODEL
        self.dimension: Optional[int] = None

    def _load_model(self):
        """Lazy-load the embedding model."""
        if self._model is None:
            logger.info(f"Loading embedding model: {self._model_name}")
            try:
                from sentence_transformers import SentenceTransformer
                self._model = SentenceTransformer(self._model_name)
                # Determine embedding dimension
                test_embed = self._model.encode(["test"])
                self.dimension = test_embed.shape[1]
                logger.info(f"✅ Embedding model loaded — dimension: {self.dimension}")
            except ImportError:
                raise ImportError(
                    "sentence-transformers not installed. "
                    "Run: pip install sentence-transformers"
                )
        return self._model

    def embed_texts(self, texts: List[str], batch_size: int = 32) -> np.ndarray:
        """
        Generate embeddings for a list of texts.
        Returns numpy array of shape (n_texts, embedding_dim).
        """
        model = self._load_model()
        logger.debug(f"Embedding {len(texts)} texts in batches of {batch_size}")
        embeddings = model.encode(
            texts,
            batch_size=batch_size,
            show_progress_bar=len(texts) > 100,
            normalize_embeddings=True,  # L2 normalize for cosine similarity
            convert_to_numpy=True,
        )
        return embeddings.astype(np.float32)

    def embed_query(self, query: str) -> np.ndarray:
        """Embed a single query string. Returns shape (1, dim)."""
        return self.embed_texts([query])

    @property
    def is_loaded(self) -> bool:
        return self._model is not None

    def get_dimension(self) -> int:
        if self.dimension is None:
            self._load_model()
        return self.dimension


embedding_service = EmbeddingService()
