from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from config import bot


@bot.command_handler()
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Greets user and shows bot info"""

    msg = f"Hello {update.effective_sender.first_name}! I am a bot that uses dictionary apis! More features will be added in the future as I am currently still a work in progress!"

    photo = await context.bot.get_user_profile_photos(context.bot.id)
    photo = photo.photos[0][-1]

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("All Commands", callback_data="start/help")]
    ])

    if update.message:
        await update.message.reply_photo(photo, msg, reply_markup=keyboard)


@bot.query_handler("start")
async def start_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    btn = query.data.removeprefix("start/")

    if btn == "help":
        msg = await help(update, context)
        if update.effective_message.text:
            await update.effective_message.edit_text(msg)
        else:
            await update.effective_message.edit_caption(msg)


@bot.command_handler()
async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Shows all available commands"""

    command_list = [f"/{command.command} - {command.description}" for _, command in bot.commands]
    msg = "All commands:\n" + "\n".join(command_list)

    chat_id = update.effective_chat.id
    thread_id = update.message.message_thread_id if update.message else None

    if update.message: 
        await context.bot.send_message(chat_id=chat_id, message_thread_id=thread_id, text=msg)
    
    else:
        return msg