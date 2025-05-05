from telegram import Update, LinkPreviewOptions
from telegram.ext import ContextTypes

from config import bot, Button
from api import FormattedData


def get_kb_types(button: dict = {">>": "spword/next_cjt"}):
    cjts_types_kb = {
        "participles": Button.new((
            {"Indicative": "spword/indicative", "Subjunctive": "spword/subjunctive"},
            {"Perfect": "spword/perfect", "Perfect Subjunctive": "spword/perfect_subjunctive"},
            {"Affirmative Imperative": "spword/affirmative_imperative"},
            {"Return to Word": "spword/return"}
        )),
        "indicative": Button.new((
            {"Participles": "spword/participles", "Subjunctive": "spword/subjunctive"},
            {"Perfect": "spword/perfect", "Perfect Subjunctive": "spword/perfect_subjunctive"},
            {"Affirmative Imperative": "spword/affirmative_imperative"},
            button,
            {"Return to Word": "spword/return"}
        )),
        "subjunctive": Button.new((
            {"Participles": "spword/participles", "Indicative": "spword/indicative"},
            {"Perfect": "spword/perfect", "Perfect Subjunctive": "spword/perfect_subjunctive"},
            {"Affirmative Imperative": "spword/affirmative_imperative"},
            button,
            {"Return to Word": "spword/return"}
        )),
        "perfect": Button.new((
            {"Participles": "spword/participles", "Indicative": "spword/indicative"},
            {"Subjunctive": "spword/subjunctive", "Perfect Subjunctive": "spword/perfect_subjunctive"},
            {"Affirmative Imperative": "spword/affirmative_imperative"},
            button,
            {"Return to Word": "spword/return"}
        )),
        "perfect_subjunctive": Button.new((
            {"Participles": "spword/participles", "Indicative": "spword/indicative"},
            {"Subjunctive": "spword/subjunctive", "Perfect": "spword/perfect"},
            {"Affirmative Imperative": "spword/affirmative_imperative"},
            button,
            {"Return to Word": "spword/return"}
        )),
        "affirmative_imperative": Button.new((
            {"Participles": "spword/participles", "Indicative": "spword/indicative"},
            {"Subjunctive": "spword/subjunctive", "Perfect": "spword/perfect"},
            {"Perfect Subjunctive": "spword/perfect_subjunctive"},
            {"Return to Word": "spword/return"}
        )),
    }
    return cjts_types_kb


def spword_keyboard(
        data: list, current_page: int,
        next: str, prev: str,
        has_cjts: bool = False, is_cjts: bool = False,
        key: str = "participles", start: int = 0, end: int = 0
):

    if has_cjts:
        if len(data) == 1:
            keyboard = Button.new((
                {"Conjugate": "spword/conjugate"},
            ))

        elif current_page == 0:
            keyboard = Button.new((
                {">>": f"spword/{next}"},
                {"Conjugate": "spword/conjugate"}
            ))

        elif current_page == len(data)-1:
            keyboard = Button.new((
                {"<<": f"spword/{prev}"},
                {"Conjugate": "spword/conjugate"}
            ))

        else:
            keyboard = Button.new((
                {"<<": f"spword/{prev}", ">>": f"spword/{next}"},
                {"Conjugate": "spword/conjugate"}
            ))

    elif is_cjts:
        if current_page == 0:
            keyboard = Button.new((
                {">>": f"spword/{next}"},
                {"Return to Word": "spword/return"}
            ))

            keyboard = get_kb_types({">>": f"spword/{next}"})[key]

        elif current_page == end:
            keyboard = Button.new((
                {"<<": f"spword/{prev}"},
                {"Return to Word": "spword/return"}
            ))

            keyboard = get_kb_types({"<<": f"spword/{prev}"})[key]
        elif current_page == start:
            keyboard = get_kb_types({">>": f"spword/{next}"})[key]

        else:
            keyboard = Button.new((
                {"<<": f"spword/{prev}", ">>": f"spword/{next}"},
                {"Return to Word": "spword/return"}
            ))

            keyboard = get_kb_types({"<<": f"spword/{prev}", ">>": f"spword/{next}"})[key]

    else:
        if current_page == 0:
            keyboard = Button.new((
                {">>": f"spword/{next}"},
            ))

        elif current_page == len(data)-1:
            keyboard = Button.new((
                {"<<": f"spword/{prev}"},
            ))

        else:
            keyboard = Button.new((
                {"<<": f"spword/{prev}", ">>": f"spword/{next}"},
            ))

    return keyboard


@bot.query_handler()
async def spword(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    btn = query.data.removeprefix("spword/")
    msg_id = update.effective_message.id

    if btn == "next_def":
        data: FormattedData = context.chat_data[f"{msg_id}|data"]
        context.chat_data[f"{msg_id}|current_def"] += 1
        current_page: int = context.chat_data[f"{msg_id}|current_def"]

        msg = f"Page {current_page+1} of {len(data.definitions)}\n\n{data.definitions[current_page]}"
        has_cjts = context.chat_data[f"{msg_id}|request"][current_page].has_cjts
        keyboard = spword_keyboard(data.definitions, current_page, "next_def", "prev_def", has_cjts=has_cjts)
    
    elif btn == "prev_def":
        data: FormattedData = context.chat_data[f"{msg_id}|data"]
        context.chat_data[f"{msg_id}|current_def"] -= 1
        current_page: int = context.chat_data[f"{msg_id}|current_def"]

        msg = f"Page {current_page+1} of {len(data.definitions)}\n\n{data.definitions[current_page]}"
        has_cjts = context.chat_data[f"{msg_id}|request"][current_page].has_cjts
        keyboard = spword_keyboard(data.definitions, current_page, "next_def", "prev_def", has_cjts=has_cjts)
    
    elif btn == "next_cjt":
        data: FormattedData = context.chat_data[f"{msg_id}|data"]
        context.chat_data[f"{msg_id}|current_cjt"] += 1
        current_page: int = context.chat_data[f"{msg_id}|current_def"]
        current_cjt: int = context.chat_data[f"{msg_id}|current_cjt"]
        key = context.chat_data[f"{msg_id}|current_key"]
        if key == "participles":
            end = 0
        elif key == "indicative":
            end = 5
        elif key == "subjunctive":
            end = 8
        elif key == "perfect":
            end = 13
        elif key == "perfect_subjunctive":
            end = 16
        else:
            end = 17

        msg = f"{data.conjugations[current_page][current_cjt]}"
        keyboard = spword_keyboard(data.conjugations[current_page], current_cjt, "next_cjt", "prev_cjt", is_cjts=True, key=key, end=end)
    
    elif btn == "prev_cjt":
        data: FormattedData = context.chat_data[f"{msg_id}|data"]
        context.chat_data[f"{msg_id}|current_cjt"] -= 1
        current_page: int = context.chat_data[f"{msg_id}|current_def"]
        current_cjt: int = context.chat_data[f"{msg_id}|current_cjt"]
        key = context.chat_data[f"{msg_id}|current_key"]
        if key == "participles":
            start = 0
        elif key == "indicative":
            start = 1
        elif key == "subjunctive":
            start = 6
        elif key == "perfect":
            start = 9
        elif key == "perfect_subjunctive":
            start = 14
        else:
            start = 17

        msg = f"{data.conjugations[current_page][current_cjt]}"
        keyboard = spword_keyboard(data.conjugations[current_page], current_cjt, "next_cjt", "prev_cjt", is_cjts=True, key=key, start=start)
    
    elif btn == "conjugate":
        data: FormattedData = context.chat_data[f"{msg_id}|data"]
        current_page: int = context.chat_data[f"{msg_id}|current_def"]
        current_cjt = context.chat_data[f"{msg_id}|current_cjt"] = 0
        context.chat_data[f"{msg_id}|current_key"] = "participles"

        msg = f"{data.conjugations[current_page][current_cjt]}"
        keyboard = get_kb_types()["participles"]
    
    elif btn == "participles":
        data: FormattedData = context.chat_data[f"{msg_id}|data"]
        context.chat_data[f"{msg_id}|current_cjt"] = 0
        current_page: int = context.chat_data[f"{msg_id}|current_def"]
        current_cjt: int = context.chat_data[f"{msg_id}|current_cjt"]
        key = context.chat_data[f"{msg_id}|current_key"] = btn

        msg = f"{data.conjugations[current_page][current_cjt]}"
        keyboard = get_kb_types()[btn]
    
    elif btn == "indicative":
        data: FormattedData = context.chat_data[f"{msg_id}|data"]
        context.chat_data[f"{msg_id}|current_cjt"] = 1
        current_page: int = context.chat_data[f"{msg_id}|current_def"]
        current_cjt: int = context.chat_data[f"{msg_id}|current_cjt"]
        key = context.chat_data[f"{msg_id}|current_key"] = btn

        msg = f"{data.conjugations[current_page][current_cjt]}"
        keyboard = get_kb_types()[btn]

    elif btn == "subjunctive":
        data: FormattedData = context.chat_data[f"{msg_id}|data"]
        context.chat_data[f"{msg_id}|current_cjt"] = 6
        current_page: int = context.chat_data[f"{msg_id}|current_def"]
        current_cjt: int = context.chat_data[f"{msg_id}|current_cjt"]
        key = context.chat_data[f"{msg_id}|current_key"] = btn

        msg = f"{data.conjugations[current_page][current_cjt]}"
        keyboard = get_kb_types()[btn]
    
    elif btn == "perfect":
        data: FormattedData = context.chat_data[f"{msg_id}|data"]
        context.chat_data[f"{msg_id}|current_cjt"] = 9
        current_page: int = context.chat_data[f"{msg_id}|current_def"]
        current_cjt: int = context.chat_data[f"{msg_id}|current_cjt"]
        key = context.chat_data[f"{msg_id}|current_key"] = btn

        msg = f"{data.conjugations[current_page][current_cjt]}"
        keyboard = get_kb_types()[btn]
    
    elif btn == "perfect_subjunctive":
        data: FormattedData = context.chat_data[f"{msg_id}|data"]
        context.chat_data[f"{msg_id}|current_cjt"] = 14
        current_page: int = context.chat_data[f"{msg_id}|current_def"]
        current_cjt: int = context.chat_data[f"{msg_id}|current_cjt"]
        key = context.chat_data[f"{msg_id}|current_key"] = btn

        msg = f"{data.conjugations[current_page][current_cjt]}"
        keyboard = get_kb_types()[btn]
    
    elif btn == "affirmative_imperative":
        data: FormattedData = context.chat_data[f"{msg_id}|data"]
        context.chat_data[f"{msg_id}|current_cjt"] = 17
        current_page: int = context.chat_data[f"{msg_id}|current_def"]
        current_cjt: int = context.chat_data[f"{msg_id}|current_cjt"]
        key = context.chat_data[f"{msg_id}|current_key"] = btn

        msg = f"{data.conjugations[current_page][current_cjt]}"
        keyboard = get_kb_types()[btn]
    
    elif btn == "return":
        data: FormattedData = context.chat_data[f"{msg_id}|data"]
        current_page: int = context.chat_data[f"{msg_id}|current_def"]
        has_cjts = context.chat_data[f"{msg_id}|request"][current_page].has_cjts

        msg = f"Page {current_page+1} of {len(data.definitions)}\n\n{data.definitions[current_page]}"
        keyboard = spword_keyboard(data.definitions, current_page, "next_def", "prev_def", has_cjts=has_cjts)

    await update.effective_message.edit_text(msg, reply_markup=keyboard, link_preview_options=LinkPreviewOptions(is_disabled=False))


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
        keyboard = Button.new((
            {">>": "page/next"},
        ))

    elif current_page == len(data)-1:
        keyboard = Button.new((
            {"<<": "page/prev"},
        ))

    else:
        keyboard = Button.new((
            {"<<": "page/prev", ">>": "page/next"},
        ))

    msg = f"Page {current_page+1} of {len(data)}\n\n{data[current_page]}"

    await update.effective_message.edit_text(msg, reply_markup=keyboard)