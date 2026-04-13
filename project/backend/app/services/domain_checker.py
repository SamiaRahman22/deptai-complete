"""
Domain Restriction Service.
Determines if a query is department-related using keyword heuristics
plus optional embedding-based semantic similarity.
"""

from dataclasses import dataclass
from typing import List
import re
from loguru import logger
from app.core.config import settings


@dataclass
class DomainResult:
    is_in_domain: bool
    score: float
    method: str
    matched_keywords: List[str]


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

# Domain-positive terms (any match = likely in domain)
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
    def __init__(self):
        self._reject_patterns = [re.compile(p, re.IGNORECASE) for p in HARD_REJECT_PATTERNS]
        self._positive_words = set(w.lower() for w in DOMAIN_POSITIVE)

    async def check(self, query: str) -> DomainResult:
        """Check if the query is department-domain relevant."""
        query_lower = query.lower()
        words = re.findall(r"\b\w+\b", query_lower)

        # 1. Hard reject check
        for pattern in self._reject_patterns:
            if pattern.search(query_lower):
                return DomainResult(
                    is_in_domain=False,
                    score=0.0,
                    method="hard_reject",
                    matched_keywords=[],
                )

        # 2. Keyword overlap scoring
        matched = [w for w in words if w in self._positive_words]
        keyword_score = min(len(matched) / max(len(words), 1) * 3, 1.0)

        # 3. Short academic queries are usually in-domain
        # e.g. "cgpa?" or "thesis deadline?"
        if len(words) <= 6 and any(w in self._positive_words for w in words):
            keyword_score = max(keyword_score, 0.6)

        is_in_domain = keyword_score >= settings.DOMAIN_THRESHOLD

        logger.debug(
            f"Domain check: score={keyword_score:.2f} matched={matched[:5]} in_domain={is_in_domain}"
        )

        return DomainResult(
            is_in_domain=is_in_domain,
            score=round(keyword_score, 3),
            method="keyword",
            matched_keywords=matched[:10],
        )


domain_checker = DomainChecker()
