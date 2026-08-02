"""
Language Detector for CurricuAlign AI Preprocessing Pipeline.
Filters out non-English job descriptions to ensure clean AI skill extraction.
"""

import re
import logging
from typing import Tuple, Set

logger = logging.getLogger("industry_engine.processing.language_detector")


class LanguageDetector:
    """
    Lightweight, fast English language validator for job descriptions.
    """

    # Top English stop words for fast heuristic language scoring
    ENGLISH_STOP_WORDS: Set[str] = {
        "the", "and", "to", "of", "a", "in", "is", "that", "for", "it",
        "as", "was", "with", "be", "by", "on", "not", "he", "i", "this",
        "are", "or", "an", "they", "from", "at", "has", "have", "will",
        "our", "you", "we", "work", "experience", "team", "skills", "role",
        "position", "developer", "engineer", "software", "data", "requirements",
        "seeking", "join", "looking", "responsibilities", "qualifications"
    }

    # German/French/Spanish indicators for quick rejection
    NON_ENGLISH_INDICATORS: Set[str] = {
        "und", "der", "die", "das", "mit", "für", "sind", "werden", "wir", "suchen", "einen", "erfahrenen", "unser", "bereich", "ihre", "aufgaben", "kenntnisse", # German
        "et", "du", "de", "des", "pour", "dans", "est", "une", "avec", "nous", "vous", "recherchons", # French
        "los", "las", "del", "por", "para", "como", "con", "una", "este", "buscamos", "experiencia" # Spanish
    }

    WORD_TOKEN_RE = re.compile(r"\b[a-zA-ZäöüßÄÖÜáéíóúÁÉÍÓÚàèìòùÀÈÌÒÙâêîôûÂÊÎÔÛ]{2,}\b")

    def is_english(self, text: str, min_english_ratio: float = 0.15) -> Tuple[bool, str, float]:
        """
        Determines whether the given text is English based on vocabulary density.
        Returns tuple: (is_english: bool, detected_lang: str, confidence_score: float).
        """
        if not text or not text.strip():
            return False, "unknown", 0.0

        tokens = [token.lower() for token in self.WORD_TOKEN_RE.findall(text)]
        if not tokens:
            return False, "unknown", 0.0

        total_words = len(tokens)
        english_match_count = sum(1 for token in tokens if token in self.ENGLISH_STOP_WORDS)
        non_english_match_count = sum(1 for token in tokens if token in self.NON_ENGLISH_INDICATORS)

        # 1. Reject if clear non-English indicators found
        if non_english_match_count >= 2 or (non_english_match_count > english_match_count and non_english_match_count > 0):
            return False, "non_english", round(english_match_count / total_words, 3)

        english_ratio = english_match_count / total_words

        # 2. Accept if ratio meets threshold, or has English words with 0 non-English indicators (Tech descriptions)
        if english_ratio >= min_english_ratio or non_english_match_count == 0 or (english_match_count >= 2 and total_words <= 40):
            return True, "en", round(english_ratio, 3)

        return False, "unsupported_or_low_confidence", round(english_ratio, 3)
