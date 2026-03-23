from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def main_menu_keyboard() -> InlineKeyboardMarkup:
    """Returns an inline keyboard with common shortcuts."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="📊 Health", callback_data="cmd_health"),
            InlineKeyboardButton(text="📚 Labs", callback_data="cmd_labs"),
        ],
        [
            InlineKeyboardButton(text="❓ Help", callback_data="cmd_help"),
        ],
    ])
