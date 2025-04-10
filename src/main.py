from telegram import Update
from telegram.ext import ContextTypes
from config import bot


@bot.command()
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = "Hello! I am a bot created by oden. Do /help for a list of commands!"
    await context.bot.send_message(chat_id=update.effective_chat.id, text=msg)


@bot.command()
async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Shows all commands"""
    msg = "All commands:\n" + "\n".join(bot.commands)
    await context.bot.send_message(chat_id=update.effective_chat.id, text=msg)


if __name__ == "__main__":
    bot.run()
