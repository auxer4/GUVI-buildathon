import nltk
from nltk.sentiment import SentimentIntensityAnalyzer

nltk.download("vader_lexicon", quiet=True)
sia = SentimentIntensityAnalyzer()

SCAM_KEYWORDS = [
    "urgent", "verify", "otp", "account blocked",
    "click", "refund", "prize", "lottery", "winner"
]


def extract_text_features(text: str) -> dict:
    lower_text = text.lower()

    keyword_hits = sum(1 for k in SCAM_KEYWORDS if k in lower_text)
    sentiment = sia.polarity_scores(text)["compound"]
    exclamations = text.count("!")
    capital_ratio = sum(1 for c in text if c.isupper()) / max(len(text), 1)

    return {
        "keyword_hits": keyword_hits,
        "sentiment": sentiment,
        "exclamation_count": exclamations,
        "capital_ratio": round(capital_ratio, 3),
        "text_length": len(text)
    }
