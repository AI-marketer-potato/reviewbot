import re

HANGUL_RANGE = re.compile(r"[\uAC00-\uD7AF]")
HIRAGANA_RANGE = re.compile(r"[\u3040-\u309F]")
KATAKANA_RANGE = re.compile(r"[\u30A0-\u30FF]")
CJK_RANGE = re.compile(r"[\u4E00-\u9FFF]")  # Common CJK ideographs


def detect_country_by_text(text: str, default: str = "USA") -> str:
    """Rudimentary detection of likely country code from text script.
    - Returns 'KOR' if Hangul present
    - Returns 'JPN' if Hiragana/Katakana present (or strong CJK without Hangul)
    - Otherwise returns default (e.g., 'USA')
    """
    if not text:
        return default
    if HANGUL_RANGE.search(text):
        return "KOR"
    if HIRAGANA_RANGE.search(text) or KATAKANA_RANGE.search(text):
        return "JPN"
    # If contains CJK but not Hangul, assume Japanese for our locales
    if CJK_RANGE.search(text):
        return "JPN"
    return default 