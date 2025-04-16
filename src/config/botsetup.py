import os
import importlib
from enum import Enum, auto
from typing import Callable
from telegram import BotCommandScope, BotCommand, Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ConversationHandler, filters, CallbackQueryHandler


class EntryType(Enum):
    COMMANDHANDLER = auto()
    QUERYHANDLER = auto()
    MESSAGEHANDLER = auto()


class Bot:
    commands: list[tuple[str, BotCommand]] = []

    def __init__(self, token: str):
        self.app = (
            ApplicationBuilder()
            .token(token)
            .post_init(self.post_init)
            .post_stop(self.post_stop)
            .build()
        )

    @staticmethod
    async def post_init(app):
        grouped_commands: dict[str, list[BotCommand]] = {scope: [] for scope, _ in Bot.commands}

        for scope, command in Bot.commands:
            grouped_commands[scope].append(command)

        for scope, command in grouped_commands.items():
            await app.bot.set_my_commands(command, BotCommandScope(scope))

        print(f"Logged in as {app.bot.first_name}.\nSynced {len(Bot.commands)} commands.")

    @staticmethod
    async def post_stop(app):
        scopes = {scope for scope, _ in Bot.commands}

        for scope in scopes:
            await app.bot.delete_my_commands(BotCommandScope(scope))

        print(f"Logging off...")

    def command_handler(self, command_name="", description="", scope=BotCommandScope.DEFAULT):
        def decorator(func: Callable):
            name = command_name or func.__name__
            handler = CommandHandler(name, func)
            self.app.add_handler(handler)
            self.commands.append((scope, BotCommand(name, description or func.__doc__ or "No description provided")))
            return func
        return decorator

    def query_handler(self, query_name=""):
        def decorator(func: Callable):
            name = query_name or func.__name__
            handler = CallbackQueryHandler(func, f"{name}/[A-Za-z0-9]+")
            self.app.add_handler(handler)
            return func
        return decorator

    def message_handler(self, msg_filter=filters.ALL):
        def decorator(func: Callable):
            handler = MessageHandler(msg_filter, func)
            self.app.add_handler(handler)
            return func
        return decorator

    def conversation_handler(self, entry_type: EntryType, states: dict, fallbacks: list, cmd_name: str="", extra_entry_points: list|None=None, scope=BotCommandScope.DEFAULT, msg_filter=None):
        """Decorated function will be first entry point"""
        def decorator(func: Callable):

            if entry_type == EntryType.COMMANDHANDLER:
                name = cmd_name or func.__name__
                cmd_handler = CommandHandler(name, func, msg_filter)
                entry_points = [cmd_handler] + extra_entry_points if extra_entry_points else [cmd_handler]
                self.commands.append((scope, BotCommand(name, func.__doc__ or "No description provided")))

            elif entry_type == EntryType.QUERYHANDLER:
                name = cmd_name or func.__name__
                query_handler = CallbackQueryHandler(func, f"{name}/[A-Za-z0-9]+")
                entry_points = [query_handler] + extra_entry_points if extra_entry_points else [query_handler]

            elif entry_type == EntryType.MESSAGEHANDLER:
                msg_handler = MessageHandler(msg_filter, func)
                entry_points = [msg_handler] + extra_entry_points if extra_entry_points else [msg_handler]

            else:
                raise TypeError("Invalid entry type")

            handler = ConversationHandler(entry_points=entry_points, states=states, fallbacks=fallbacks)
            self.app.add_handler(handler)
            return func
        return decorator

    def run(self):
        self.app.run_polling(allowed_updates=Update.ALL_TYPES)


def load_handlers():
    for filename in os.listdir("./src/handlers"):
        if filename.endswith(".py"):
            importlib.import_module(f"handlers.{filename[:-3]}")