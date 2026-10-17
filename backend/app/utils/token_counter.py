def estimate_tokens(text: str) -> int:
    """Estimate input tokens using a simple character-based approximation."""
    return max(1, len(text) // 4) if text else 0
