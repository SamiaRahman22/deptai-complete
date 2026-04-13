"""
Structured Knowledge Retrieval Service.
Searches FAQs and Procedures using simple text matching + scoring.
This is the "structured" half of the hybrid pipeline.
"""

import re
from typing import Optional
from sqlalchemy.orm import Session
from loguru import logger

from app.models.faq import FAQ
from app.models.procedure import Procedure


class StructuredRetrieval:
    """
    Retrieves relevant FAQs and Procedures for a given query.
    Uses token overlap scoring (fast, no embeddings needed for structured data).
    """

    def _tokenize(self, text: str):
        return set(re.findall(r"\b\w+\b", text.lower()))

    def _score(self, query_tokens: set, text: str) -> float:
        text_tokens = self._tokenize(text)
        if not text_tokens:
            return 0.0
        overlap = query_tokens & text_tokens
        return len(overlap) / (len(query_tokens) + 1e-6)

    async def retrieve(self, query: str, db: Session, top_n: int = 3) -> Optional[str]:
        """
        Returns a formatted string of the most relevant FAQs and procedures.
        Returns None if nothing relevant is found.
        """
        query_tokens = self._tokenize(query)
        context_parts = []

        # ── FAQs ──
        faqs = db.query(FAQ).filter(FAQ.is_active == True).all()
        faq_scores = []
        for faq in faqs:
            score = self._score(query_tokens, faq.question + " " + faq.answer)
            if score > 0.05:
                faq_scores.append((score, faq))

        faq_scores.sort(key=lambda x: x[0], reverse=True)
        top_faqs = faq_scores[:top_n]

        if top_faqs:
            faq_text = "### Relevant FAQs\n"
            for _, faq in top_faqs:
                faq_text += f"**Q: {faq.question}**\nA: {faq.answer}\n\n"
                # Increment usage count
                try:
                    faq.usage_count = (faq.usage_count or 0) + 1
                    db.commit()
                except Exception:
                    db.rollback()
            context_parts.append(faq_text)

        # ── Procedures ──
        procedures = db.query(Procedure).filter(Procedure.is_active == True).all()
        proc_scores = []
        for proc in procedures:
            full_text = proc.title + " " + (proc.description or "") + " " + " ".join(proc.steps)
            score = self._score(query_tokens, full_text)
            if score > 0.05:
                proc_scores.append((score, proc))

        proc_scores.sort(key=lambda x: x[0], reverse=True)
        top_procs = proc_scores[:2]

        if top_procs:
            proc_text = "### Relevant Procedures\n"
            for _, proc in top_procs:
                steps_formatted = "\n".join(f"  {i+1}. {s}" for i, s in enumerate(proc.steps))
                proc_text += f"**{proc.title}** ({proc.category})\n{steps_formatted}\n\n"
            context_parts.append(proc_text)

        if not context_parts:
            return None

        result = "\n".join(context_parts)
        logger.debug(f"Structured retrieval found {len(top_faqs)} FAQs, {len(top_procs)} procedures")
        return result


structured_retrieval = StructuredRetrieval()
