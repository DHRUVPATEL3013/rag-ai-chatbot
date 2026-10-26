"""
Conversation memory manager.

Controls when conversation summaries are created or updated.
"""

from app.memory.summary import summarize_conversation


def should_update_summary(message_count: int) -> bool:
    """
    Summary checkpoints:

        5 messages
        10 messages
        20 messages
        30 messages
        ...

    After 10 messages, update every 10 messages.
    """

    if message_count == 5:
        return True

    if message_count >= 10 and message_count % 10 == 0:
        return True

    return False


def get_summary_start_index(message_count: int) -> int:
    """
    Return the first message that needs to be incorporated
    into the existing summary.

    Example:

        5  -> 0
        10 -> 5
        20 -> 10
        30 -> 20
    """

    if message_count == 5:
        return 0

    if message_count >= 10:
        return message_count - 10

    return 0


def create_or_update_summary(
    messages: list,
    existing_summary: str | None = None,
) -> str:
    """
    Create or update the conversation summary.

    The first summary covers the first 5 messages.

    Later summaries incorporate the latest 10 messages
    into the existing summary.
    """

    if not messages:
        return existing_summary or ""

    message_count = len(messages)

    start_index = get_summary_start_index(message_count)

    messages_to_summarize = messages[start_index:]

    return summarize_conversation(
        messages=messages_to_summarize,
        existing_summary=existing_summary,
    )   