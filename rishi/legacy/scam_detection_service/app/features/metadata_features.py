import re
from app.utils.regex_patterns import URL_REGEX, PHONE_REGEX, UPI_REGEX


def extract_metadata_features(text: str) -> dict:
    urls = re.findall(URL_REGEX, text)
    phones = re.findall(PHONE_REGEX, text)
    upis = re.findall(UPI_REGEX, text)

    return {
        "url_count": len(urls),
        "phone_count": len(phones),
        "upi_count": len(upis),
        "has_url": int(len(urls) > 0),
        "has_phone": int(len(phones) > 0),
        "has_upi": int(len(upis) > 0)
    }
