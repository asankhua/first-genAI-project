"""
Data cleaning functions for Zomato restaurant fields.

Rules (from ARCHITECTURE.md):
- Price: string -> integer (strip commas, symbols).
- Rating: string -> float (handle "X.X/5" and plain numbers).
- Cuisines: string -> list of trimmed strings (comma/pipe delimited).
"""

import re
from typing import Any, List, Optional


def clean_price(value: Any) -> Optional[int]:
    """
    Convert price-like value to integer.

    Strips commas, spaces, and common currency symbols (e.g. ₹, $) then parses.
    Returns None for missing, empty, or unparseable values.

    Examples:
        "1,500" -> 1500
        "₹2,000" -> 2000
        " 500 " -> 500
    """
    if value is None:
        return None
    if isinstance(value, int):
        return value if value >= 0 else None
    if isinstance(value, float):
        if value != value or value < 0:  # NaN or negative
            return None
        return int(value)
    s = str(value).strip()
    if not s:
        return None
    # Remove commas and currency symbols (₹, $, etc.) and spaces
    cleaned = re.sub(r"[\s,₹$€£]", "", s)
    # Allow digits only (and optional leading minus, but we reject negative later)
    if not re.match(r"^-?\d+$", cleaned):
        return None
    n = int(cleaned)
    return n if n >= 0 else None


def clean_rating(value: Any) -> Optional[float]:
    """
    Extract numeric rating as float from string or number.

    Handles "X.X/5", plain numbers, and "NEW" (treated as 0.0 to retain unrated restaurants).
    Returns None for missing or invalid.

    Examples:
        "4.1/5" -> 4.1
        "4.5" -> 4.5
        "3" -> 3.0
        "NEW" -> 0.0 (retains row for max_rating=0 queries)
    """
    if value is None:
        return None
    if isinstance(value, (int, float)):
        v = float(value)
        if v != v or v < 0 or v > 5:  # NaN or out of range
            return None
        return round(v, 2)
    s = str(value).strip()
    if not s:
        return None
    # Zomato uses "NEW" for restaurants without ratings - treat as 0 to retain data
    if s.upper() == "NEW":
        return 0.0
    # Match "4.1/5" or "4.1" or "3"
    m = re.match(r"^(\d+(?:\.\d+)?)\s*(?:/\s*5)?$", s, re.IGNORECASE)
    if m:
        v = float(m.group(1))
        if 0 <= v <= 5:
            return round(v, 2)
    return None


def clean_cuisines(value: Any) -> List[str]:
    """
    Parse cuisines string into a list of trimmed, non-empty strings.

    Splits on comma or pipe, strips whitespace, drops empty entries.

    Examples:
        "North Indian, Chinese" -> ["North Indian", "Chinese"]
        "Cafe | Bakery" -> ["Cafe", "Bakery"]
        "" -> []
    """
    if value is None:
        return []
    if isinstance(value, list):
        return [str(x).strip() for x in value if str(x).strip()]
    s = str(value).strip()
    if not s:
        return []
    # Split on comma or pipe (and optional surrounding spaces)
    parts = re.split(r"\s*[,|]\s*", s)
    return [p.strip() for p in parts if p.strip()]
