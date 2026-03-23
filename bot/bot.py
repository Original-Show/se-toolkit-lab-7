import argparse
import asyncio
import sys

from handlers.standard import start_handler, help_handler
from handlers.backend import health_handler, labs_handler, scores_handler
from services.llm import route_intent

async def process_test_command(command: str):
    if command.startswith("/start"):
        print(await start_handler(command))
    elif command.startswith("/help"):
        print(await help_handler(command))
    elif command.startswith("/health"):
        print(await health_handler(command))
    elif command.startswith("/labs"):
        print(await labs_handler(command))
    elif command.startswith("/scores"):
        print(await scores_handler(command))
    else:
        print(await route_intent(command))
    sys.exit(0)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--test", type=str, help="Run a command in test mode without Telegram")
    args = parser.parse_args()

    if args.test:
        asyncio.run(process_test_command(args.test))
    else:
        from aiogram import Bot, Dispatcher, F
        from aiogram.filters import Command
        from config import settings
        from aiogram.types import Message
        
        bot = Bot(token=settings.bot_token)
        dp = Dispatcher()

        @dp.message(Command("start"))
        async def cmd_start(message: Message): await message.answer(await start_handler(message.text))
        
        @dp.message(Command("help"))
        async def cmd_help(message: Message): await message.answer(await help_handler(message.text))
        
        @dp.message(Command("health"))
        async def cmd_health(message: Message): await message.answer(await health_handler(message.text))
        
        @dp.message(Command("labs"))
        async def cmd_labs(message: Message): await message.answer(await labs_handler(message.text))
        
        @dp.message(Command("scores"))
        async def cmd_scores(message: Message): await message.answer(await scores_handler(message.text))

        @dp.message(F.text)
        async def cmd_text(message: Message):
            # Send processing message
            wait_msg = await message.answer("Thinking...")
            try:
                result = await route_intent(message.text)
                await wait_msg.edit_text(result)
            except Exception as e:
                await wait_msg.edit_text(f"Error processing your request: {e}")

        async def run_polling():
            print("Starting Telegram Bot...")
            await dp.start_polling(bot)

        asyncio.run(run_polling())

if __name__ == "__main__":
    main()
