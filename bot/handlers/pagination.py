from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, LinkPreviewOptions
from telegram.ext import ContextTypes

from config import bot


@bot.query_handler()
async def page(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    btn = query.data.removeprefix("page/")
    msg_id = update.effective_message.id
    

    if btn == "next":
        data: list = context.chat_data[f"{msg_id}|data"]
        context.chat_data[f"{msg_id}|current_page"] += 1
        current_page: int = context.chat_data[f"{msg_id}|current_page"]

    else:
        data: list = context.chat_data[f"{msg_id}|data"]
        context.chat_data[f"{msg_id}|current_page"] -= 1
        current_page: int = context.chat_data[f"{msg_id}|current_page"]
    
    if current_page == 0:
        keyboard = InlineKeyboardMarkup([[InlineKeyboardButton(">>", callback_data="page/next")]])
    
    elif current_page == len(data)-1:
        keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("<<", callback_data="page/prev")]])
        
    else:
        keyboard = InlineKeyboardMarkup([[
            InlineKeyboardButton("<<", callback_data="page/prev"),
            InlineKeyboardButton(">>", callback_data="page/next")]])
    
    msg = f"Page {current_page+1} of {len(data)}\n\n{data[current_page]}"

    await update.effective_message.edit_text(msg, reply_markup=keyboard)


@bot.query_handler()
async def spword(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    btn = query.data.removeprefix("spword/")
    msg_id = update.effective_message.id
    

    if btn == "next":
        data: list = context.chat_data[f"{msg_id}|data"]
        context.chat_data[f"{msg_id}|current_page"] += 1
        current_page: int = context.chat_data[f"{msg_id}|current_page"]

    else:
        data: list = context.chat_data[f"{msg_id}|data"]
        context.chat_data[f"{msg_id}|current_page"] -= 1
        current_page: int = context.chat_data[f"{msg_id}|current_page"]
    
    if current_page == 0:
        keyboard = InlineKeyboardMarkup([[InlineKeyboardButton(">>", callback_data="spword/next")]])
    
    elif current_page == len(data)-1:
        keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("<<", callback_data="spword/prev")]])
        
    else:
        keyboard = InlineKeyboardMarkup([[
            InlineKeyboardButton("<<", callback_data="spword/prev"),
            InlineKeyboardButton(">>", callback_data="spword/next")]])
    
    msg = f"Page {current_page+1} of {len(data)}\n\n{data[current_page]}"

    await update.effective_message.edit_text(msg, reply_markup=keyboard, link_preview_options=LinkPreviewOptions(is_disabled=False))