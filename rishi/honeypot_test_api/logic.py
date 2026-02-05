"""
Honeypot scoring logic for test API

This module implements a STUB scoring function for prototype testing.
In production, this would integrate with real ML detectors and threat intelligence.

NOTE: This is a placeholder implementation. The actual scam detection logic
lives in rishi/detectors/ with full ML/linguistic analysis capabilities.
"""

from typing import List, Dict
import re


def calculate_scam_probability(messages: List[Dict[str, str]]) -> float:
    """
    Calculate scam probability based on message patterns.
    
    THIS IS A STUB FOR PROTOTYPE TESTING.
    Real implementation uses:
    - Linguistic manipulation detector (urgency, fear, authority)
    - Behavioral pattern detector (rigidity, pressure)
    - Link intelligence (domain reputation, entropy)
    - Identity mismatch detector (brand inconsistencies)
    - Historical patterns (known bad actors)
    
    Args:
        messages: List of messages with 'sender' and 'text' keys
    
    Returns:
        Scam probability score (0-100)
    """
    
    if not messages:
        return 0.0
    
    # Initialize score
    score = 0.0
    message_count = len(messages)
    
    # Factor 1: Message volume (more messages = slightly higher suspicion)
    # Range: 0-20 points
    volume_score = min(message_count * 3, 20)
    score += volume_score
    
    # Factor 2: Detect urgency keywords (common in scams)
    # Range: 0-30 points
    urgency_keywords = [
        "urgent", "immediate", "act now", "limited time", "hurry",
        "confirm", "verify", "update", "suspended", "locked", "risk"
    ]
    urgency_count = 0
    for msg in messages:
        text = msg.get("text", "").lower()
        for keyword in urgency_keywords:
            urgency_count += text.count(keyword)
    urgency_score = min(urgency_count * 5, 30)
    score += urgency_score
    
    # Factor 3: Detect suspicious patterns
    # Range: 0-25 points
    suspicious_patterns = [
        r'\b(?:\+91[-\s]?)?[6-9]\d{9}\b',  # Phone numbers
        r'\b\w+@\w+\b',                     # UPI/Email patterns
        r'https?://[^\s]+',                 # URLs
        r'\b(?:otp|password|pin|cvv)\b'    # Sensitive data requests
    ]
    pattern_matches = 0
    for msg in messages:
        text = msg.get("text", "")
        for pattern in suspicious_patterns:
            pattern_matches += len(re.findall(pattern, text, re.IGNORECASE))
    suspicious_score = min(pattern_matches * 4, 25)
    score += suspicious_score
    
    # Factor 4: Text length analysis
    # Very short repetitive messages indicate scripted behavior
    # Range: 0-15 points
    avg_length = sum(len(msg.get("text", "")) for msg in messages) / message_count if message_count else 0
    if avg_length < 50:
        text_score = 15
    elif avg_length < 100:
        text_score = 10
    else:
        text_score = 5
    score += text_score
    
    # Factor 5: Sender pattern (multiple "scammer" sends = suspicious)
    # Range: 0-10 points
    scammer_sends = sum(1 for msg in messages if msg.get("sender", "").lower() in ["scammer", "attacker"])
    sender_score = min(scammer_sends * 2, 10)
    score += sender_score
    
    # Ensure score is within valid range [0, 100]
    final_score = min(max(score, 0), 100)
    
    return final_score


def should_trigger_handoff(scam_probability: float, threshold: int = 80) -> bool:
    """
    Determine if handoff should be triggered based on scam probability.
    
    Args:
        scam_probability: Scam score (0-100)
        threshold: Threshold score for handoff (default: 80)
    
    Returns:
        True if score >= threshold, False otherwise
    """
    return scam_probability >= threshold


def generate_response_message(scam_probability: float, handoff: bool) -> str:
    """
    Generate a human-readable message based on analysis results.
    
    Args:
        scam_probability: Scam score (0-100)
        handoff: Whether handoff is triggered
    
    Returns:
        Status message string
    """
    
    if scam_probability < 30:
        message = f"Conversation appears safe (score: {scam_probability:.1f}/100)"
    elif scam_probability < 60:
        message = f"Suspicious patterns detected (score: {scam_probability:.1f}/100). Monitoring."
    elif scam_probability < 80:
        message = f"High scam indicators (score: {scam_probability:.1f}/100). Warning user."
    else:
        message = f"Scam confirmed (score: {scam_probability:.1f}/100). Handing off to honeypot engagement."
    
    return message
