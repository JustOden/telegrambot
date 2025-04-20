from enum import Enum, auto

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, LinkPreviewOptions
from telegram.ext import ContextTypes, filters, ConversationHandler, CommandHandler, MessageHandler

from config import bot, EntryType
from api import SpanishWord


class State(Enum):
    WORD_SEARCH = auto()
    CONJUGATE = auto()


async def word(update: Update, context: ContextTypes.DEFAULT_TYPE):
    word = update.message.text
    data: list = SpanishWord.get(word)
    current_page: int = 0
    msg =f"Page {current_page+1} of {len(data)}\n\n{data[current_page]}"
    
    if len(data) > 1:
        keyboard = InlineKeyboardMarkup([[InlineKeyboardButton(">>", callback_data="spword/next")]])

    else:
        keyboard = None

    chat_id = update.effective_chat.id
    thread_id = update.message.message_thread_id
    msg = await context.bot.send_message(chat_id=chat_id, message_thread_id=thread_id, text=msg, reply_markup=keyboard, link_preview_options=LinkPreviewOptions(is_disabled=False))
    context.chat_data[f"{msg.id}|data"] = data
    context.chat_data[f"{msg.id}|current_page"] = current_page


async def verb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    word = update.message.text
    data: list = SpanishWord.conjugate_verb(word)
    current_page: int = 0
    msg =f"Page {current_page+1} of {len(data)}\n\n{data[current_page]}"
    
    if len(data) > 1:
        keyboard = InlineKeyboardMarkup([[InlineKeyboardButton(">>", callback_data="page/next")]])

    else:
        keyboard = None

    chat_id = update.effective_chat.id
    thread_id = update.message.message_thread_id
    msg = await context.bot.send_message(chat_id=chat_id, message_thread_id=thread_id, text=msg, reply_markup=keyboard)
    context.chat_data[f"{msg.id}|data"] = data
    context.chat_data[f"{msg.id}|current_page"] = current_page


async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.effective_chat.send_message("Stopped listening for words... returning to /spdict")
    await spdict_command(update, context)
    return ConversationHandler.END


@bot.command_handler(command_name="spdict")
async def spdict_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """English-Spanish dictionary"""

    msg = "Welcome to spdict, a Spanish dictionary!\nSelect an option from below:"

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("Search Word", callback_data="spdict/word"),
            InlineKeyboardButton("Conjugate Verb", callback_data="spdict/conjugate")
        ],
        [InlineKeyboardButton("Show All Commands", callback_data="start/help")]])

    await update.effective_chat.send_message(msg, reply_markup=keyboard)


@bot.conversation_handler(
    cmd_name="spdict",
    entry_type=EntryType.QUERYHANDLER,
    states={
        State.WORD_SEARCH: [MessageHandler(filters.TEXT & ~filters.COMMAND, word)],
        State.CONJUGATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, verb)]
    },
    fallbacks=[CommandHandler("stop", stop)]
)
async def spdict_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    btn = query.data.removeprefix("spdict/")

    if btn == "word":
        await query.answer("Enter word to search...")
        await update.effective_message.edit_text("Enter word to search or /stop:")
        return State.WORD_SEARCH

    if btn == "conjugate":
        await query.answer("Enter verb to conjugate...")
        await update.effective_message.edit_text("Enter verb to conjugate or /stop:")
        return State.CONJUGATE