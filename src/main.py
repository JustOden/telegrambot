from telegram import Update
from telegram.ext import ContextTypes
from config import bot


@bot.command()
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Greets user and shows bot info"""
    msg = f"Hello {update.effective_sender.first_name}! I am a bot created by t.me/justoden. I am still a work in progress. Do /help for a list of commands!"
    await context.bot.send_message(chat_id=update.effective_chat.id, text=msg)


@bot.command()
async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Shows all commands"""
    command_list = [f"{command} - {description}" for command, description in bot.commands.items()]
    msg = "All commands:\n" + "\n".join(command_list)
    await context.bot.send_message(chat_id=update.effective_chat.id, text=msg)


if __name__ == "__main__":
    bot.run()
