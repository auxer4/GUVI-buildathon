"""
LLM-powered extraction for scam intelligence.
Placeholder with mock LLM for development.
"""

import logging
import json
import re
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)


def llm_extract(text: str, entity_types: Optional[List[str]] = None) -> List[Dict[str, Any]]:
    """
    Extract entities using LLM (with fallback to heuristics).
    Placeholder for actual OpenAI/Claude integration.

    Args:
        text: Text to extract from
        entity_types: Optional list of entity types to extract (e.g., ["bank", "amount", "relationship"])

    Returns:
        List of extracted entities with confidence
    """
    try:
        # For now, use heuristic-based extraction
        # In production, this would call OpenAI, Claude, or local LLM
        entities = []

        # Extract amounts/money
        amount_entities = _extract_amounts(text)
        if amount_entities:
            entities.extend(amount_entities)

        # Extract relationships/roles
        relationship_entities = _extract_relationships(text)
        if relationship_entities:
            entities.extend(relationship_entities)

        # Extract actions/requests
        action_entities = _extract_actions(text)
        if action_entities:
            entities.extend(action_entities)

        logger.info(f"LLM extraction found {len(entities)} entities")
        return entities

    except Exception as e:
        logger.error(f"Error in LLM extraction: {e}")
        return []


def _extract_amounts(text: str) -> List[Dict[str, Any]]:
    """Extract monetary amounts."""
    entities = []

    # Match patterns like: Rs. 1000, $5000, INR 10000, rupees 2000
    amount_patterns = [
        r'(?:rs\.?|rupees?|inr)\s*[:\-]?\s*([\d,]+)',
        r'\$\s*([\d,]+)',
        r'(?:amount|total|send|transfer)\s+(?:of\s+)?(?:rs\.?|rupees?|inr|usd)?\s*[:\-]?\s*([\d,]+)',
    ]

    for pattern in amount_patterns:
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for match in matches:
            amount_str = match.group(1).replace(',', '')
            try:
                amount = float(amount_str)
                entities.append({
                    "type": "amount",
                    "value": str(amount),
                    "currency": "INR",  # Default for India-based scams
                    "confidence": 0.85,
                    "context": match.group(0),
                    "source": "llm_heuristic",
                })
            except ValueError:
                pass

    return entities


def _extract_relationships(text: str) -> List[Dict[str, Any]]:
    """Extract relationships/roles (brother, friend, customer, etc.)."""
    entities = []

    relationship_keywords = {
        "family": ["brother", "sister", "mother", "father", "dad", "mom", "son", "daughter", "cousin", "uncle", "aunt"],
        "colleague": ["colleague", "coworker", "boss", "manager", "supervisor", "staff", "employee"],
        "friend": ["friend", "buddy", "mate", "pal"],
        "customer": ["customer", "client", "buyer", "user"],
        "victim": ["victim", "patient", "user", "person"],
    }

    text_lower = text.lower()

    for rel_type, keywords in relationship_keywords.items():
        for keyword in keywords:
            if keyword in text_lower:
                entities.append({
                    "type": "relationship",
                    "value": keyword,
                    "category": rel_type,
                    "confidence": 0.75,
                    "source": "llm_heuristic",
                })
                break

    return entities


def _extract_actions(text: str) -> List[Dict[str, Any]]:
    """Extract scammer actions/requests."""
    entities = []

    action_patterns = {
        "transfer": r"transfer|send|pay|remit",
        "verify": r"verify|confirm|authenticate|check|validate",
        "click": r"click|tap|open|visit|download",
        "login": r"login|sign in|log in|sign-in",
        "share": r"share|tell me|provide|give me|send me",
        "urgent": r"urgent|asap|quickly|immediately|now",
    }

    text_lower = text.lower()

    for action_type, pattern in action_patterns.items():
        matches = re.finditer(pattern, text_lower)
        for match in matches:
            entities.append({
                "type": "action",
                "value": match.group(0),
                "action_type": action_type,
                "confidence": 0.7,
                "source": "llm_heuristic",
            })

    return entities


def get_llm_api_key(provider: str = "openai") -> Optional[str]:
    """
    Get LLM API key from environment.
    
    Args:
        provider: LLM provider ("openai", "anthropic", "local")
        
    Returns:
        API key or None
    """
    import os

    if provider == "openai":
        return os.getenv("OPENAI_API_KEY")
    elif provider == "anthropic":
        return os.getenv("ANTHROPIC_API_KEY")
    elif provider == "local":
        return "local"

    return None


def llm_extract_with_api(
    text: str,
    provider: str = "openai",
    api_key: Optional[str] = None,
    model: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Extract entities using actual LLM API.
    Requires API keys in environment or function arguments.

    Args:
        text: Text to extract from
        provider: LLM provider ("openai", "anthropic")
        api_key: Optional API key override
        model: Optional model override

    Returns:
        List of extracted entities
    """
    try:
        if provider == "openai":
            return _extract_with_openai(text, api_key, model)
        elif provider == "anthropic":
            return _extract_with_anthropic(text, api_key, model)
        else:
            logger.warning(f"Unknown LLM provider: {provider}")
            return llm_extract(text)  # Fall back to heuristic
    except Exception as e:
        logger.error(f"Error using LLM API: {e}")
        return llm_extract(text)  # Fall back to heuristic


def _extract_with_openai(
    text: str,
    api_key: Optional[str] = None,
    model: str = "gpt-3.5-turbo",
) -> List[Dict[str, Any]]:
    """Extract using OpenAI API (stub)."""
    # This would be implemented with actual OpenAI client
    # For now, fall back to heuristic
    logger.debug("OpenAI extraction stub - using heuristic fallback")
    return llm_extract(text)


def _extract_with_anthropic(
    text: str,
    api_key: Optional[str] = None,
    model: str = "claude-opus",
) -> List[Dict[str, Any]]:
    """Extract using Anthropic Claude API (stub)."""
    # This would be implemented with actual Claude client
    # For now, fall back to heuristic
    logger.debug("Anthropic extraction stub - using heuristic fallback")
    return llm_extract(text)
