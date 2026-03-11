def summarize_tool(text: str) -> str:
    """Analyze and prepare text for summarization.

    Use this tool when the user asks to summarize text.
    It counts words and characters to help produce a concise summary.

    Args:
        text: The text content to summarize.

    Returns:
        The original text along with word and character counts.
    """
    word_count = len(text.split())
    char_count = len(text)
    return (
        f"TEXT TO SUMMARIZE ({word_count} words, {char_count} chars):\n\n"
        f"{text}\n\n"
        f"INSTRUCTION: Summarize the above text in 2-3 short, simple sentences. "
        f"Use easy words. Keep it under {max(word_count // 3, 30)} words."
    )