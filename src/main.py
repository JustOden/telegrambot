from telegram import Update
from telegram.ext import ContextTypes
from config import bot


@bot.command()
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Greets user, shows bot info and invokes help command"""
    msg = f"Hello {update.effective_sender.first_name}! I am a bot that uses dictionary apis! More features will be added in the future as I am currently still a work in progress! Here is a list of commands!"
    chat_id = update.effective_chat.id
    thread_id = update.message.message_thread_id
    await context.bot.send_message(chat_id=chat_id, message_thread_id=thread_id, text=msg)
    await help(update, context)


@bot.command()
async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Shows all currently available commands"""
    command_list = [f"/{command} - {description}" for command, description in bot.commands]
    msg = "All commands:\n" + "\n\n".join(command_list)
    chat_id = update.effective_chat.id
    thread_id = update.message.message_thread_id
    await context.bot.send_message(chat_id=chat_id, message_thread_id=thread_id, text=msg)


if __name__ == "__main__":
    bot.run()
