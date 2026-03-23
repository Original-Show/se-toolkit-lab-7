async def start_handler(text: str) -> str:
    return "Welcome to the LMS Bot! Type /help to see available commands."

async def help_handler(text: str) -> str:
    return "Available commands:\n/start - Welcome message\n/help - List commands\n/health - Backend status\n/labs - List labs\n/scores <lab> - Show scores"
