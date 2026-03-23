"""Common handler utilities shared across command handlers."""


async def format_error(error: Exception) -> str:
    """Format an error into a user-friendly message."""
    return f"⚠️ Something went wrong: {error}"
