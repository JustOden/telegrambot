import os
import importlib
from enum import Enum, auto
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters


class Event(Enum):
    ON_MESSAGE = auto()


class Bot:
    commands: list[tuple[str, str]] = []

    def __init__(self, token: str):
        self.app = ApplicationBuilder().token(token).post_init(self.on_ready).build()

    @staticmethod
    async def on_ready(app):
        await app.bot.set_my_commands(commands=Bot.commands)
        print(f"Logged in as {app.bot.first_name}.\nSynced {len(Bot.commands)} commands.")

    def command(self, command_name: str="", description: str=""):
        def decorator(func):
            name = command_name or func.__name__
            handler = CommandHandler(name, func)
            self.app.add_handler(handler)
            self.commands.append((name, description or func.__doc__ or "No description provided"))
            return func
        return decorator

    def event(self, event_type: Event):
        def decorator(func):
            if event_type == Event.ON_MESSAGE:
                handler = MessageHandler(filters.ALL, func)
                self.app.add_handler(handler)
        return decorator

    def run(self):
        self.app.run_polling()


def load_handlers():
    for filename in os.listdir("./src/handlers"):
        if filename.endswith(".py") and not filename.startswith("__"):
            importlib.import_module(f"handlers.{filename[:-3]}")