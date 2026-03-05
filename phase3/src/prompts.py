"""
Prompt template: user inputs + candidate restaurants -> LLM prompt for recommendations.
"""

from typing import Any, Dict, List, Optional


def build_recommendation_prompt(
    place: str,
    min_rating: float,
    max_price: Optional[int],
    cuisine: Optional[str],
    candidates: List[Dict[str, Any]],
    top_n: int = 5,
    name_key: str = "name",
) -> str:
    """
    Build the user-facing prompt for the LLM.

    Args:
        place: User's location filter.
        min_rating: User's minimum rating.
        max_price: User's max price (optional).
        cuisine: User's cuisine preference (optional).
        candidates: Filtered list of restaurant dicts (each with rating, price, cuisines, name_key).
        top_n: Ask LLM to return this many recommendations.
        name_key: Key for restaurant name in each candidate dict.

    Returns:
        Single string to send as user message (system message can be separate).
    """
    lines = [
        "I am looking for restaurant recommendations with the following criteria:",
        f"- Place: {place}",
        f"- Minimum rating: {min_rating}",
    ]
    if max_price is not None:
        lines.append(f"- Maximum budget for two people: {max_price}")
    if cuisine and cuisine.strip():
        lines.append(f"- Preferred cuisine: {cuisine}")

    lines.append("")
    lines.append("Here are some matching restaurants from the dataset (name, rating, price for two, cuisines):")
    for i, r in enumerate(candidates[:30], 1):  # cap for context
        name = r.get(name_key) or r.get("restaurant name") or "Unknown"
        rating = r.get("rating", "?")
        price = r.get("price") if r.get("price") is not None else "?"
        cuisines = r.get("cuisines")
        cuisines_str = ", ".join(cuisines) if isinstance(cuisines, list) else str(cuisines or "?")
        lines.append(f"  {i}. {name} | Rating: {rating} | Price: {price} | Cuisines: {cuisines_str}")

    lines.append("")
    lines.append(
        f"From the list above, recommend the top {top_n} options for me. "
        "First, write one welcoming sentence summarizing the area and top picks (e.g. 'You\'re in for a treat in [place] with these fantastic finds - [names] - which offer...'). "
        "Then, for each recommendation, give the restaurant name and a short reason why it fits my criteria. "
        "Use this format exactly, one per line: \"- <Restaurant Name>: <reason>\""
    )
    return "\n".join(lines)


def system_prompt() -> str:
    """System message for the recommendation LLM."""
    return (
        "You are a helpful restaurant recommendation assistant. "
        "You only recommend from the list of restaurants provided. "
        "Keep responses concise and use the requested format."
    )
