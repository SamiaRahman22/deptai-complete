"""
Enhanced Domain Restriction Service.
Uses multi-layer approach: semantic + keyword + context.
Returns confidence scores instead of binary yes/no.
"""

from dataclasses import dataclass
from typing import List
import re
import numpy as np
from loguru import logger
from app.core.config import settings


@dataclass
class DomainResult:
    """Result of domain check with confidence score."""
    is_in_domain: bool
    confidence_score: float  # 0-1, higher = more confident
    method: str  # "semantic", "keyword", "context", "hard_reject"
    matched_keywords: List[str]
    should_escalate: bool  # True if low confidence + ambiguous


# Hard-reject phrases — clearly off-topic
HARD_REJECT_PATTERNS = [
    r"\b(weather|forecast|rain|sunny|temperature)\b",
    r"\b(recipe|cook|food|restaurant|eat|drink)\b",
    r"\b(sports|football|cricket|match|score|game)\b",
    r"\b(movie|film|show|series|netflix|watch)\b",
    r"\b(stock|crypto|bitcoin|invest|market)\b",
    r"\b(joke|funny|meme|laugh|humor)\b",
    r"\b(relationship|girlfriend|boyfriend|dating|love)\b",
    r"\b(political|election|vote|party|president)\b",
    r"\btranslat(e|ion|or)\b",
    r"\b(poem|song|lyric|music|play)\b",
]

# Domain-positive terms
DOMAIN_POSITIVE = settings.domain_keywords_list + [
    "department", "university", "college", "study", "student", "teacher",
    "class", "assignment", "quiz", "project", "internship", "cgpa", "gpa",
    "semester", "credit", "course", "curriculum", "syllabus", "prerequisite",
    "registration", "enrollment", "drop", "add", "waiver", "appeal",
    "scholarship", "financial", "tuition", "fee", "notice", "circular",
    "thesis", "dissertation", "research", "lab", "laboratory", "dean",
    "advisor", "supervisor", "faculty", "professor", "lecturer", "ta",
    "office", "form", "document", "certificate", "transcript", "result",
    "grade", "mark", "exam", "final", "mid", "quiz", "attendance",
    "deadline", "schedule", "timetable", "calendar", "holiday",
]


class DomainChecker:
    """
    Multi-layer domain checking with confidence scoring.
    
    Layers:
    1. Hard reject (0.0 confidence for obvious off-topic)
    2. Keyword scoring (based on domain term overlap)
    3. Semantic boundary check (if embedder available)
    4. Context length analysis
    """

    def __init__(self):
        self._reject_patterns = [re.compile(p, re.IGNORECASE) for p in HARD_REJECT_PATTERNS]
        self._positive_words = set(w.lower() for w in DOMAIN_POSITIVE)
        self._embedder = None

    def _get_embedder(self):
        """Lazy-load embedder for semantic checking."""
        if self._embedder is None:
            try:
                from app.rag.embedder import embedding_service
                self._embedder = embedding_service
            except:
                self._embedder = False  # Mark as unavailable
        return self._embedder if self._embedder else None

    async def check(self, query: str) -> DomainResult:
        """
        Check if query is department-domain relevant with confidence scoring.
        
        Returns confidence in range [0, 1]:
        - 0.0-0.3: Out of domain (reject)
        - 0.3-0.6: Unclear (suggest rephrase, but allow)
        - 0.6-0.8: Likely domain (answer with caveat)
        - 0.8-1.0: Clearly domain (answer confidently)
        """
        query_lower = query.lower()
        words = re.findall(r"\b\w+\b", query_lower)

        # LAYER 1: Hard reject check
        for pattern in self._reject_patterns:
            if pattern.search(query_lower):
                logger.info(f"Domain check: HARD REJECT (pattern matched)")
                return DomainResult(
                    is_in_domain=False,
                    confidence_score=0.0,
                    method="hard_reject",
                    matched_keywords=[],
                    should_escalate=False,
                )

        # LAYER 2: Keyword-based scoring
        keyword_score = self._get_keyword_score(query, words)

        # LAYER 3: Semantic boundary check (if available)
        semantic_score = await self._get_semantic_score(query)

        # LAYER 4: Context length analysis
        context_score = self._get_context_score(query, words)

        # Combine scores (weighted average)
        combined_score = (
            0.4 * keyword_score +  # 40% keyword matching
            0.3 * semantic_score +  # 30% semantic similarity
            0.3 * context_score     # 30% context analysis
        )

        # Determine routing
        is_in_domain = combined_score >= settings.DOMAIN_THRESHOLD
        matched = [w for w in words if w in self._positive_words]
        
        # Should escalate if low confidence and ambiguous
        should_escalate = (combined_score < 0.5) and (len(matched) > 0)

        logger.debug(
            f"Domain check: keyword={keyword_score:.2f}, semantic={semantic_score:.2f}, "
            f"context={context_score:.2f}, combined={combined_score:.2f}, "
            f"in_domain={is_in_domain}, should_escalate={should_escalate}"
        )

        return DomainResult(
            is_in_domain=is_in_domain,
            confidence_score=round(combined_score, 3),
            method="multi_layer",
            matched_keywords=matched[:10],
            should_escalate=should_escalate,
        )

    def _get_keyword_score(self, query: str, words: List[str]) -> float:
        """Score based on domain keyword overlap."""
        if not words:
            return 0.0
        
        matched = [w for w in words if w in self._positive_words]
        keyword_score = min(len(matched) / max(len(words), 1) * 3, 1.0)
        
        # Boost for short academic queries (e.g., "cgpa?")
        if len(words) <= 6 and matched:
            keyword_score = max(keyword_score, 0.6)
        
        return keyword_score

    async def _get_semantic_score(self, query: str) -> float:
        """
        Score based on semantic similarity to domain.
        Uses embedding model to check if query is semantically close to dept.
        """
        embedder = self._get_embedder()
        if not embedder or not embedder.is_loaded:
            return 0.3  # Neutral score if embedder not available
        
        try:
            # Embed query and compare to example domain queries
            query_embedding = embedder.embed_query(query)
            
            domain_examples = [
                "What courses should I take?",
                "When is the exam?",
                "How do I register?",
                "Who is my advisor?",
                "What's the deadline?",
            ]
            domain_embeddings = embedder.embed_texts(domain_examples)
            
            # Calculate average similarity to domain examples
            similarities = []
            for domain_emb in domain_embeddings:
                # Cosine similarity
                sim = np.dot(query_embedding[0], domain_emb)
                similarities.append(sim)
            
            avg_similarity = np.mean(similarities)
            # Normalize to [0, 1]
            semantic_score = max(0, min(1, (avg_similarity + 1) / 2))
            
            return semantic_score
        except Exception as e:
            logger.warning(f"Semantic scoring failed: {e}")
            return 0.3

    def _get_context_score(self, query: str, words: List[str]) -> float:
        """Score based on query structure and context."""
        # Longer, more specific queries are usually better
        length_score = min(len(words) / 20, 1.0)  # Cap at 20 words
        
        # Queries with question marks are usually domain-related
        question_bonus = 0.2 if "?" in query else 0.0
        
        context_score = (length_score * 0.5) + question_bonus
        return min(context_score, 1.0)


domain_checker = DomainChecker()