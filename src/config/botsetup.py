import os
import importlib
from enum import Enum, auto
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters

OWNER_ID = os.getenv("OWNER_ID")


class Event(Enum):
    ON_MESSAGE = auto()


class Bot:
    commands: dict[str, str] = {}

    def __init__(self, token: str):
        self.app = ApplicationBuilder().token(token).post_init(self.on_ready).build()
    
    @staticmethod
    async def on_ready(app):
        await app.bot.send_message(text="Online", chat_id=OWNER_ID)

    def command(self, command_name: str=""):
        def decorator(func):
            name = func.__name__ if not command_name else command_name
            handler = CommandHandler(name, func)
            self.app.add_handler(handler)
            self.commands[f"/{name}"] = func.__doc__ if func.__doc__ else "No description provided"
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