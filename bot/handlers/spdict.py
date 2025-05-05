from telegram import Update, LinkPreviewOptions
from telegram.ext import ContextTypes, filters, ConversationHandler, CommandHandler, MessageHandler

from config import bot, EntryType, Button
from api import SpanishDict, WordRequest, FormattedData


async def search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text: str = update.message.text
    request: WordRequest = SpanishDict.request(text)
    data: FormattedData = SpanishDict.format(request)
    current_page: int = 0
    msg = f"Page {current_page+1} of {len(data.definitions)}\n\n{data.definitions[current_page]}"

    if request[current_page].has_cjts and len(request) > 1:
        keyboard = Button.new((
            {">>": "spword/next_def"},
            {"Conjugate": "spword/conjugate"}
        ))

    elif request[current_page].has_cjts:
        keyboard = Button.new((
            {"Conjugate": "spword/conjugate"},
        ))

    elif len(request) > 1:
        keyboard = Button.new((
            {">>": "spword/next_def"},
        ))

    else:
        keyboard = None

    chat_id = update.effective_chat.id
    thread_id = update.message.message_thread_id
    msg = await context.bot.send_message(
        chat_id=chat_id, message_thread_id=thread_id, text=msg, reply_markup=keyboard,
        link_preview_options=LinkPreviewOptions(is_disabled=False)
    )

    context.chat_data[f"{msg.id}|request"] = request
    context.chat_data[f"{msg.id}|data"] = data
    context.chat_data[f"{msg.id}|current_def"] = current_page
    context.chat_data[f"{msg.id}|current_cjt"] = current_page


async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.effective_chat.send_message("Stopped listening for words...")
    return ConversationHandler.END


@bot.conversation_handler(
    cmd_name="spdict", entry_type=EntryType.COMMANDHANDLER,
    states={1: [MessageHandler(filters.TEXT & ~filters.COMMAND, search)]},
    fallbacks=[CommandHandler("stop", stop)]
)
async def spdict_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """English-Spanish dictionary"""
    await update.effective_chat.send_message("Enter word to search or /stop:")
    return 1