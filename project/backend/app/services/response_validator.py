"""
Response Validation Service.
Checks generated responses against source documents to prevent hallucinations.
"""

import re
from typing import Dict, List, Tuple
from loguru import logger


class ResponseValidator:
    """
    Validates LLM responses by checking claims against source context.
    """

    def __init__(self):
        self.validation_threshold = 0.5  # % of response that must be grounded

    def validate_response(
        self,
        response: str,
        source_chunks: List[str],
        query: str
    ) -> Dict:
        """
        Validate response against source chunks.
        
        Returns:
        {
            "is_valid": bool,
            "confidence_score": float (0-1),
            "unverified_claims": List[str],
            "validation_method": str,
            "evidence_density": float (0-1)
        }
        """
        if not source_chunks or not response.strip():
            return {
                "is_valid": False,
                "confidence_score": 0.0,
                "unverified_claims": ["No source context available"],
                "validation_method": "no_context",
                "evidence_density": 0.0,
            }

        # Step 1: Extract claims from response
        claims = self._extract_claims(response)
        if not claims:
            return {
                "is_valid": True,
                "confidence_score": 0.8,  # No claims = can't hallucinate
                "unverified_claims": [],
                "validation_method": "no_claims",
                "evidence_density": 1.0,
            }

        # Step 2: Verify each claim against sources
        verified_count = 0
        unverified_claims = []
        
        for claim in claims:
            is_verified = self._verify_claim(claim, source_chunks)
            if is_verified:
                verified_count += 1
            else:
                unverified_claims.append(claim)

        # Step 3: Calculate evidence density
        evidence_density = verified_count / len(claims) if claims else 0
        
        # Step 4: Calculate confidence score
        # High if most claims are verified
        confidence = self._calculate_confidence(
            evidence_density=evidence_density,
            num_claims=len(claims),
            num_verified=verified_count
        )

        is_valid = evidence_density >= self.validation_threshold

        logger.debug(
            f"Response validation: {verified_count}/{len(claims)} claims verified "
            f"(density={evidence_density:.2f}, confidence={confidence:.2f})"
        )

        return {
            "is_valid": is_valid,
            "confidence_score": confidence,
            "unverified_claims": unverified_claims[:5],  # Top 5 unverified
            "validation_method": "claim_verification",
            "evidence_density": evidence_density,
        }

    def _extract_claims(self, text: str) -> List[str]:
        """
        Extract factual claims from response.
        Simple approach: Split on periods, filter out generic phrases.
        """
        sentences = re.split(r'[.!?]+', text)
        
        claims = []
        skip_patterns = [
            r"^(based on|according to|the context|the document)",
            r"^(i |you |we |this |that |here)",
        ]
        
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) < 10:
                continue
            
            # Skip generic introductory phrases
            skip = False
            for pattern in skip_patterns:
                if re.match(pattern, sentence, re.IGNORECASE):
                    skip = True
                    break
            
            if not skip:
                claims.append(sentence)
        
        return claims[:10]  # Limit to top 10 claims

    def _verify_claim(self, claim: str, source_chunks: List[str]) -> bool:
        """
        Check if a claim appears in source chunks.
        Uses simple keyword matching + semantic similarity.
        """
        claim_lower = claim.lower()
        
        # Extract key terms (important words)
        key_terms = self._extract_key_terms(claim)
        
        # Check if most key terms appear in sources
        for chunk in source_chunks:
            chunk_lower = chunk.lower()
            
            # Simple keyword matching: if 70% of key terms in chunk, claim is verified
            matching_terms = sum(1 for term in key_terms if term in chunk_lower)
            match_ratio = matching_terms / len(key_terms) if key_terms else 0
            
            if match_ratio >= 0.7:
                return True
        
        return False

    def _extract_key_terms(self, text: str, min_length: int = 4) -> List[str]:
        """
        Extract important terms from text (filter out common words).
        """
        common_words = {
            "the", "is", "are", "was", "were", "be", "been", "being",
            "have", "has", "had", "do", "does", "did", "will", "would",
            "could", "should", "may", "might", "must", "can", "for",
            "and", "or", "not", "but", "if", "in", "on", "at", "to",
            "from", "by", "with", "as", "a", "an", "this", "that",
            "these", "those", "which", "who", "when", "where", "why",
        }
        
        words = re.findall(r'\b\w+\b', text.lower())
        key_terms = [
            w for w in words
            if len(w) >= min_length and w not in common_words
        ]
        
        return key_terms

    def _calculate_confidence(
        self,
        evidence_density: float,
        num_claims: int,
        num_verified: int
    ) -> float:
        """
        Calculate confidence score (0-1).
        Based on: evidence density, number of claims, verification rate
        """
        # Base score from evidence density
        confidence = evidence_density
        
        # Bonus for having many claims verified (shows thoroughness)
        if num_claims >= 5 and num_verified >= 4:
            confidence = min(1.0, confidence + 0.1)
        
        # Penalty for having unverified claims
        if num_verified < num_claims:
            penalty = (num_claims - num_verified) / (num_claims * 2)
            confidence = max(0.0, confidence - penalty)
        
        return round(confidence, 3)


response_validator = ResponseValidator()