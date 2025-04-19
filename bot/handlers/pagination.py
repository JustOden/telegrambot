from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes

from config import bot


@bot.query_handler("page")
async def pagination(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    btn = query.data.removeprefix("page/")
    msg_id = update.effective_message.id
    
    if btn == "beginning":
        data: list = context.chat_data[f"{msg_id}|data"]
        context.chat_data[f"{msg_id}|current_page"] = 0
        current_page: int = context.chat_data[f"{msg_id}|current_page"]

    elif btn == "next":
        data: list = context.chat_data[f"{msg_id}|data"]
        context.chat_data[f"{msg_id}|current_page"] += 1
        current_page: int = context.chat_data[f"{msg_id}|current_page"]

    elif btn == "prev":
        data: list = context.chat_data[f"{msg_id}|data"]
        context.chat_data[f"{msg_id}|current_page"] -= 1
        current_page: int = context.chat_data[f"{msg_id}|current_page"]
    
    else:
        data: list = context.chat_data[f"{msg_id}|data"]
        context.chat_data[f"{msg_id}|current_page"] = len(data)-1
        current_page: int = context.chat_data[f"{msg_id}|current_page"]
    
    if current_page == 0:
        keyboard = InlineKeyboardMarkup([[
            InlineKeyboardButton(">", callback_data="page/next"),
            InlineKeyboardButton(">>", callback_data="page/end")]])
    
    elif current_page == len(data)-1:
        keyboard = InlineKeyboardMarkup([[
            InlineKeyboardButton("<<", callback_data="page/beginning"),
            InlineKeyboardButton("<", callback_data="page/prev")]])
        
    else:
        keyboard = InlineKeyboardMarkup([[
            InlineKeyboardButton("<<", callback_data="page/beginning"),
            InlineKeyboardButton("<", callback_data="page/prev"),
            InlineKeyboardButton(">", callback_data="page/next"),
            InlineKeyboardButton(">>", callback_data="page/end")]])
    
    msg = f"Page {current_page+1} of {len(data)}\n\n{data[current_page]}"

    await update.effective_message.edit_text(msg, reply_markup=keyboard)