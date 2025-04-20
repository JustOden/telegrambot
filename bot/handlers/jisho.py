from enum import Enum, auto

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, MessageHandler, CommandHandler, ConversationHandler, filters

from config import bot, EntryType
from api import Jisho


class State(Enum):
    WORD_SEARCH = auto()
    KANJI_SEARCH = auto()
    EXAMPLES_SEARCH = auto()
    TOKEN_SEARCH = auto()


async def word(update: Update, context: ContextTypes.DEFAULT_TYPE):
    word = update.message.text
    data: list = Jisho.word_search(word)
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


async def kanji(update: Update, context: ContextTypes.DEFAULT_TYPE):
    word = update.message.text
    data: list = Jisho.kanji_search(word)
    current_page: int = 0
    msg = data[current_page]

    if len(data) > 1:
        keyboard = InlineKeyboardMarkup([[InlineKeyboardButton(">>", callback_data="page/next")]])
    else:
        keyboard = None

    chat_id = update.effective_chat.id
    thread_id = update.message.message_thread_id
    msg = await context.bot.send_message(chat_id=chat_id, message_thread_id=thread_id, text=msg, reply_markup=keyboard)
    context.chat_data[f"{msg.id}|data"] = data
    context.chat_data[f"{msg.id}|current_page"] = current_page


async def examples(update: Update, context: ContextTypes.DEFAULT_TYPE):
    word = update.message.text
    data: list = Jisho.examples_search(word)
    current_page: int = 0
    msg = data[current_page]

    if len(data) > 1:
        keyboard = InlineKeyboardMarkup([[InlineKeyboardButton(">>", callback_data="page/next")]])
    else:
        keyboard = None

    chat_id = update.effective_chat.id
    thread_id = update.message.message_thread_id
    msg = await context.bot.send_message(chat_id=chat_id, message_thread_id=thread_id, text=msg, reply_markup=keyboard)
    context.chat_data[f"{msg.id}|data"] = data
    context.chat_data[f"{msg.id}|current_page"] = current_page


async def token(update: Update, context: ContextTypes.DEFAULT_TYPE):
    word = update.message.text
    data: list = Jisho.token_search(word)
    current_page: int = 0
    msg = data[current_page]

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
    await update.effective_chat.send_message("Stopped listening for words... returning to /jisho")
    await jisho_command(update, context)
    return ConversationHandler.END


@bot.command_handler(command_name="jisho")
async def jisho_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """English-Japanese dictionary"""

    msg = "Welcome to jisho, a Japanese dictionary!\nSelect an option from below:"

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("Search Word", callback_data="jisho/word"),
            InlineKeyboardButton("Search Kanji", callback_data="jisho/kanji")
        ],
        [
            InlineKeyboardButton("Search Examples", callback_data="jisho/examples"),
            InlineKeyboardButton("Search Token", callback_data="jisho/token")
        ],
        [InlineKeyboardButton("Show All Commands", callback_data="start/help")]])

    await update.effective_chat.send_message(msg, reply_markup=keyboard)


@bot.conversation_handler(
    cmd_name="jisho",
    entry_type=EntryType.QUERYHANDLER,
    states={
        State.WORD_SEARCH: [MessageHandler(filters.TEXT & ~filters.COMMAND, word)],
        State.KANJI_SEARCH: [MessageHandler(filters.TEXT & ~filters.COMMAND, kanji)],
        State.EXAMPLES_SEARCH: [MessageHandler(filters.TEXT & ~filters.COMMAND, examples)],
        State.TOKEN_SEARCH: [MessageHandler(filters.TEXT & ~filters.COMMAND, token)],
    },
    fallbacks=[CommandHandler("stop", stop)]
)
async def jisho_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    btn = query.data.removeprefix("jisho/")

    if btn == "word":
        await query.answer("Enter word to search...")
        await update.effective_message.edit_text("Enter word to search or /stop:")
        return State.WORD_SEARCH

    if btn == "kanji":
        await query.answer("Enter kanji to search...")
        await update.effective_message.edit_text("Enter kanji to search or /stop:")
        return State.KANJI_SEARCH
    
    if btn == "examples":
        await query.answer("Enter word to search examples...")
        await update.effective_message.edit_text("Enter word to search examples for or /stop:")
        return State.EXAMPLES_SEARCH
    
    if btn == "token":
        await query.answer("Enter sentence to tokenize...")
        await update.effective_message.edit_text("Enter Japanese sentence to tokenize or /stop:")
        return State.TOKEN_SEARCH