"""
RAG Pipeline Orchestrator.
Coordinates: Extraction → Chunking → Embedding → FAISS Indexing → Retrieval
"""

from dataclasses import dataclass
from typing import List, Optional
from loguru import logger

from app.rag.extractor import extract_text, clean_text
from app.rag.chunker import chunk_text
from app.rag.embedder import embedding_service
from app.rag.vector_store import vector_store, IndexedChunk
from app.core.config import settings


@dataclass
class IndexResult:
    chunk_count: int
    page_count: int
    source: str


@dataclass
class RetrievalResult:
    chunks: List[str]
    sources: List[str]
    scores: List[float]


class RAGPipeline:
    """
    Full RAG pipeline:
    
    INDEXING:
      document file → extract text → clean → chunk → embed → FAISS store
    
    RETRIEVAL:
      query → embed → FAISS search → return top-k chunks + sources
    """

    def __init__(self):
        self.is_ready = False

    async def initialize(self):
        """Load existing FAISS index or prepare for fresh indexing."""
        # Try to load existing index
        if vector_store.load():
            self.is_ready = True
            logger.info(f"✅ RAG pipeline ready ({vector_store.total_chunks} chunks in index)")
        else:
            logger.info("No existing FAISS index found — will be created on first document upload")
            self.is_ready = False

    async def index_document(self, file_path: str, file_type: str, doc_id: int = None) -> IndexResult:
        """
        Full indexing pipeline for a single document.
        
        Steps:
        1. Extract text from file
        2. Clean text
        3. Split into chunks
        4. Embed chunks
        5. Add to FAISS index
        6. Save index
        """
        source = file_path.split("/")[-1]
        logger.info(f"📄 Indexing: {source}")

        # Step 1: Extract
        raw_text, page_count = extract_text(file_path, file_type)
        if not raw_text.strip():
            raise ValueError(f"No text extracted from {source}")

        # Step 2: Clean
        text = clean_text(raw_text)

        # Step 3: Chunk
        chunks = chunk_text(text, source=source)
        if not chunks:
            raise ValueError(f"No chunks generated from {source}")

        logger.info(f"  Generated {len(chunks)} chunks from {page_count} pages")

        # Step 4: Embed
        chunk_texts = [c.text for c in chunks]
        embeddings = embedding_service.embed_texts(chunk_texts)

        # Step 5: Initialize index if needed
        if vector_store._index is None:
            vector_store.initialize(dimension=embeddings.shape[1])

        # Step 6: Add to index
        indexed_chunks = [
            IndexedChunk(
                text=c.text,
                source=source,
                chunk_index=c.index,
                doc_id=doc_id,
            )
            for c in chunks
        ]
        vector_store.add_embeddings(embeddings, indexed_chunks)

        # Step 7: Save
        vector_store.save()
        self.is_ready = True

        logger.info(f"  ✅ Indexed {len(chunks)} chunks from {source}")
        return IndexResult(chunk_count=len(chunks), page_count=page_count, source=source)

    async def retrieve(self, query: str, top_k: int = None) -> RetrievalResult:
        """
        Retrieve most relevant chunks for a query using semantic search.
        
        Steps:
        1. Embed the query
        2. Search FAISS index
        3. Return top-k chunks with sources
        """
        if not self.is_ready:
            return RetrievalResult(chunks=[], sources=[], scores=[])

        top_k = top_k or settings.TOP_K_RESULTS

        # Embed query
        query_embedding = embedding_service.embed_query(query)

        # FAISS search
        results = vector_store.search(query_embedding, top_k=top_k)

        if not results:
            return RetrievalResult(chunks=[], sources=[], scores=[])

        chunks = []
        sources = []
        scores = []

        seen_sources = set()
        for chunk, score in results:
            chunk_text = f"[Source: {chunk.source}]\n{chunk.text}"
            chunks.append(chunk_text)
            scores.append(score)
            if chunk.source not in seen_sources:
                sources.append(chunk.source)
                seen_sources.add(chunk.source)

        logger.debug(f"Retrieved {len(chunks)} chunks (top score: {scores[0]:.3f})")
        return RetrievalResult(chunks=chunks, sources=sources, scores=scores)

    def save_index(self):
        """Save the FAISS index on shutdown."""
        if vector_store.is_ready:
            vector_store.save()


rag_pipeline = RAGPipeline()
