"""
Utility Functions for Text Normalization and Preprocessing.
"""

import re
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)


def normalize_text(text: str) -> str:
    """
    Normalize text for analysis.
    - Convert to lowercase
    - Remove extra whitespace
    - Remove special characters (but keep space and letters/digits)

    Args:
        text: Raw text to normalize

    Returns:
        Normalized text
    """
    if not text:
        return ""

    # Convert to lowercase
    text = text.lower()

    # Remove URLs
    text = re.sub(r"https?://\S+", "", text)

    # Remove email addresses
    text = re.sub(r"\S+@\S+", "", text)

    # Remove extra whitespace
    text = re.sub(r"\s+", " ", text).strip()

    return text


def extract_keywords(text: str, min_length: int = 3) -> List[str]:
    """
    Extract meaningful keywords from text.
    Filters out common stop words.

    Args:
        text: Text to extract from
        min_length: Minimum keyword length

    Returns:
        List of keywords
    """
    stop_words = {
        "the",
        "a",
        "an",
        "and",
        "or",
        "but",
        "in",
        "on",
        "at",
        "to",
        "for",
        "of",
        "with",
        "is",
        "are",
        "be",
        "been",
        "being",
        "have",
        "has",
        "do",
        "does",
        "did",
        "will",
        "would",
        "could",
        "should",
        "may",
        "might",
        "must",
        "can",
        "i",
        "you",
        "he",
        "she",
        "it",
        "we",
        "they",
        "this",
        "that",
        "these",
        "those",
    }

    text = normalize_text(text)
    words = text.split()

    keywords = [
        w for w in words if len(w) >= min_length and w not in stop_words and w.isalpha()
    ]

    return keywords


def calculate_similarity(text1: str, text2: str) -> float:
    """
    Calculate Jaccard similarity between two texts.

    Args:
        text1: First text
        text2: Second text

    Returns:
        Similarity score [0.0, 1.0]
    """
    keywords1 = set(extract_keywords(text1))
    keywords2 = set(extract_keywords(text2))

    if not keywords1 or not keywords2:
        return 0.0

    intersection = len(keywords1 & keywords2)
    union = len(keywords1 | keywords2)

    return intersection / union if union > 0 else 0.0


def extract_sentences(text: str) -> List[str]:
    """
    Split text into sentences.

    Args:
        text: Text to split

    Returns:
        List of sentences
    """
    # Split on common sentence delimiters
    sentences = re.split(r"[.!?\n]+", text)
    # Clean and filter empty sentences
    sentences = [s.strip() for s in sentences if s.strip()]
    return sentences


def count_character_types(text: str) -> dict:
    """
    Count different character types in text.

    Args:
        text: Text to analyze

    Returns:
        Dictionary with counts of letters, digits, special chars
    """
    result = {
        "letters": 0,
        "digits": 0,
        "special": 0,
        "whitespace": 0,
    }

    for char in text:
        if char.isalpha():
            result["letters"] += 1
        elif char.isdigit():
            result["digits"] += 1
        elif char.isspace():
            result["whitespace"] += 1
        else:
            result["special"] += 1

    return result


def has_excessive_caps(text: str, threshold: float = 0.3) -> bool:
    """
    Check if text has excessive capital letters.
    Typically used in scam messages.

    Args:
        text: Text to check
        threshold: Proportion of caps considered excessive (0.0-1.0)

    Returns:
        True if excessive caps detected
    """
    letters = [c for c in text if c.isalpha()]
    if not letters:
        return False

    caps_count = sum(1 for c in letters if c.isupper())
    caps_ratio = caps_count / len(letters)

    return caps_ratio > threshold


def has_excessive_punctuation(text: str, threshold: float = 0.1) -> bool:
    """
    Check if text has excessive punctuation.

    Args:
        text: Text to check
        threshold: Proportion of punctuation considered excessive (0.0-1.0)

    Returns:
        True if excessive punctuation detected
    """
    punctuation = "!?.,;:\'\"()-"
    punct_count = sum(1 for c in text if c in punctuation)
    punct_ratio = punct_count / len(text) if text else 0

    return punct_ratio > threshold
