import re

def extract_entities(text: str) -> dict:
    """
    Extracts actionable scam intelligence from text using regex patterns.
    Returns a dictionary with lists of extracted entities, removing duplicates.
    """
    # WHY: Regex-based extraction is efficient and reliable for identifying key scam indicators.
    entities = {
        "phones": [],
        "upis": [],
        "urls": [],
        "banks": []
    }

    # Phone numbers: Matches 10-digit Indian phone numbers (common in scams).
    # WHY: Scammers often provide fake or real phone contacts for follow-up.
    phone_pattern = r'\b(?:\+91[-\s]?)?[6-9]\d{9}\b'
    entities["phones"] = list(set(re.findall(phone_pattern, text)))

    # UPI IDs: Matches patterns like user@bank (e.g., john@paytm).
    # WHY: UPI is a common payment method in India, targeted by scammers.
    upi_pattern = r'\b\w+@\w+\b'
    entities["upis"] = list(set(re.findall(upi_pattern, text)))

    # URLs: Matches HTTP/HTTPS links.
    # WHY: Scammers share malicious or phishing URLs to trick victims.
    url_pattern = r'(https?://[^\s]+|www\.[^\s]+)'
    entities["urls"] = list(set(re.findall(url_pattern, text)))

    # Bank account numbers: Matches 10-16 digit sequences (common account lengths).
    # WHY: Scammers request or provide bank details for fraudulent transfers.
    bank_pattern = r'\b\d{12,18}\b'
    entities["banks"] = list(set(re.findall(bank_pattern, text)))

    return entities
