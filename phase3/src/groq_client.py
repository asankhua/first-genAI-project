"""
Groq LLM client: call Groq API for chat completion.
"""

import os
from typing import Optional

# Default model for recommendations (fast and capable)
DEFAULT_MODEL = "llama-3.3-70b-versatile"


def get_completion(
    user_prompt: str,
    system_prompt: Optional[str] = None,
    model: str = DEFAULT_MODEL,
    temperature: float = 0.3,
    max_tokens: int = 1024,
) -> str:
    """
    Call Groq chat completions API and return the assistant message content.

    Args:
        user_prompt: The user message (e.g. from build_recommendation_prompt).
        system_prompt: Optional system message. If None, a generic one is used.
        model: Groq model id.
        temperature: 0-1. Lower = more deterministic.
        max_tokens: Max response length.

    Returns:
        Content of the first choice message.

    Raises:
        ValueError: If GROQ_API_KEY is not set.
        Exception: On API or network errors (from groq SDK).
    """
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key or not api_key.strip():
        raise ValueError(
            "GROQ_API_KEY is not set. Set it in your environment or .env file."
        )

    from groq import Groq

    client = Groq(api_key=api_key.strip())

    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": user_prompt})

    response = client.chat.completions.create(
        messages=messages,
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
    )

    if not response.choices:
        return ""
    return (response.choices[0].message.content or "").strip()
