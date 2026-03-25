"""
Ultron v3 — Response Formatter
Maps response types to Discord-formatted strings.
"""


def format_response(content: str, response_type: str) -> str:
    """
    Format a response for Discord based on its type.

    Args:
        content: The raw response text
        response_type: One of CONVERSATIONAL, TASK_COMPLETE, TASK_STARTED,
                       PROGRESS, FILE_READY, MORNING_BRIEFING

    Returns:
        Formatted Discord message string
    """
    formatters = {
        "CONVERSATIONAL": lambda c: c,
        "TASK_COMPLETE": lambda c: f"✅ **Task Complete**\n\n{c}",
        "TASK_STARTED": lambda c: f"🚀 **Task Started**\n\n{c}",
        "PROGRESS": lambda c: f"🔄 **Progress Update**\n\n{c}",
        "FILE_READY": lambda c: f"📄 **File Ready**\n\n{c}",
        "MORNING_BRIEFING": lambda c: f"☀️ **Morning Briefing**\n\n{c}",
        "ERROR": lambda c: f"⚠️ **Error**\n\n{c}",
    }

    formatter = formatters.get(response_type, formatters["CONVERSATIONAL"])
    return formatter(content)
