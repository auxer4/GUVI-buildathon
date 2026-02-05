import hashlib
import json

def sha256_from_string(value: str) -> str:
    """
    Generate SHA-256 hash from a string.
    """
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def sha256_from_dict(data: dict) -> str:
    """
    Deterministic hash from dictionary.
    Sorting keys ensures reproducibility.
    """
    canonical = json.dumps(data, sort_keys=True, separators=(",", ":"))
    return sha256_from_string(canonical)
