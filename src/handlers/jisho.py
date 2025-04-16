import re
import json
from enum import Enum, auto
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, MessageHandler, CommandHandler, ConversationHandler, filters
from jisho_api.word import Word
from jisho_api.kanji import Kanji
from jisho_api.sentence import Sentence
from jisho_api.tokenize import Tokens
from config import bot, EntryType

URL = "https://jisho.org/search/"


class State(Enum):
    WORD_SEARCH = auto()
    KANJI_SEARCH = auto()
    EXAMPLES_SEARCH = auto()
    TOKEN_SEARCH = auto()


class Jisho:
    def word_search(arg: str) -> list:
        request = Word.request(arg)

        if not request:
            return [f"No word found for {arg}."]

        entries = json.loads(request.json())
        results = [item for item in entries["data"]]
        data = []

        add_nl = lambda s: "\n" + s
        join_c = lambda s: ", ".join(s)
        bold_i = lambda s: s
        add_i = lambda s: s

        for result in results:
            word = _word if (_word:=result["japanese"][0]["word"]) else result["japanese"][0]["reading"]
            reading = _reading if word and (_reading:=result["japanese"][0]["reading"]) else ""

            fq = "common word" if result["is_common"] else ""
            jlpt = join_c(_jlpt) if (_jlpt:=result["jlpt"]) else ""
            tags = join_c(_tags) if (_tags:=result["tags"]) else ""

            joined = add_nl(f"`{_joined}`") if (_joined:=join_c([i for i in (fq, jlpt, tags) if i])) else ""
            base = f"{word}【{reading}】{joined}\n"

            for index, senses in enumerate(result["senses"], start=1):
                parts_of_speech = add_nl(bold_i(join_c(_parts_of_speech))) if (_parts_of_speech:=senses["parts_of_speech"]) else ""
                links = _links if (_links:=senses["links"]) else ""

                english_definitions = join_c(senses["english_definitions"])
                tags = join_c(_tags) if (_tags:=senses["tags"]) else ""
                restrictions = "Only applies to " + join_c(_restrictions) if (_restrictions:=senses["restrictions"]) else ""

                _see_also = "".join(senses["see_also"])
                see_also_link = URL + ("%20".join(_see_also.split()))
                see_also = f"see also [{_see_also}]({see_also_link})" if _see_also else ""

                info = join_c(_info) if (_info:=senses["info"]) else ""
                joined = add_nl(_joined) if (_joined:=join_c([i for i in (tags, restrictions, see_also, info) if i])) else ""
                base += f"{parts_of_speech}\n{index}. {english_definitions}{joined}"

                if links:
                    list_ = []

                    for link in links:
                        text = link["text"]
                        url = link["url"]
                        text_url = f"[{text}]({url})"
                        list_.append(text_url)

                    base += add_nl(add_i("\n".join(list_)))

                base += "\n"

            if len(_japanese:=result["japanese"]) > 1:
                list_ = []

                for dict_ in _japanese[1:]:
                    other_word = _word if (_word:=dict_["word"]) else dict_["reading"]
                    other_reading = f"【{dict_['reading']}】" if dict_["word"] else ""
                    other_form = f"{other_word}{other_reading}"
                    list_.append(other_form)

                base += "\nOther forms\n" + "、".join(list_)

            if len(base) > 1015:
                base = base[:1015] + " [...]"

            data.append(base)

        return data


    def find_kanji(arg: str) -> list:
        # Regex pattern for Kanji (CJK Ideographs)
        kanji_pattern = re.compile(r'[\u4E00-\u9FFF]')
        return kanji_pattern.findall(arg)


    def kanji_search(arg: str) -> list:
        # TODO - make hiragana, katakana, and romaji also able to do a kanji search
        if kanji:=Jisho.find_kanji(arg):
            results = [json.loads(r.json()) for i in kanji if (r:=Kanji.request(i))]

        else:
            return [f"No kanji found for {arg}."]

        data = []

        for result in results:
            kanji = "`Kanji`: " + result["data"]["kanji"]
            strokes = result["data"]["strokes"]

            main_meanings = "`Meanings`\n" + (", ".join(result["data"]["main_meanings"]))
            kun_readings = "\n`Kun`\n" + ("、".join(_kun)) + "\n" if (_kun:=result["data"]["main_readings"]["kun"]) else ""
            on_readings = "\n`On`\n" + ("、".join(_on)) + "\n" if (_on:=result["data"]["main_readings"]["on"]) else ""

            grade = result["data"]["meta"]["education"]["grade"]
            jlpt = result["data"]["meta"]["education"]["jlpt"]
            newspaper_rank = result["data"]["meta"]["education"]["newspaper_rank"]

            rad_alt_forms = "（" + (", ".join(_alt)) + "）" if (_alt:=result["data"]["radical"]["alt_forms"]) else ""
            rad_meaning = result["data"]["radical"]["meaning"]
            rad_parts = " `Parts`: " + (" ".join(_parts)) if (_parts:=result["data"]["radical"]["parts"]) else ""

            rad_basis = result["data"]["radical"]["basis"]
            rad_variants = " `Variants`: " + (" ".join(_variants)) if (_variants:=result["data"]["radical"]["variants"]) else ""
            rad = f" `Radical`: {rad_meaning} {rad_basis}"

            kun_examples = result["data"]["reading_examples"]["kun"]
            on_examples = result["data"]["reading_examples"]["on"]

            base = f"{kanji} `Strokes`: {strokes}\n{rad}{rad_alt_forms}{rad_parts}{rad_variants}\n`JLPT`: {jlpt}, `Taught in`: {grade}, `Newspaper rank`: {newspaper_rank}\n\n{main_meanings}\n{kun_readings}{on_readings}"

            if kun_examples:
                base += "\n`Kunyomi examples`"

                for ex in kun_examples[:3]:
                    word = ex["kanji"]
                    reading = ex["reading"]
                    meanings = ", ".join(ex["meanings"])
                    base += f"\n{word}【{reading}】\n{meanings}"

                base += "\n"

            if on_examples:
                base += "\n`Onyomi examples`"

                for ex in on_examples[:3]:
                    word = ex["kanji"]
                    reading = ex["reading"]
                    meanings = ", ".join(ex["meanings"])
                    base += f"\n{word}【{reading}】\n{meanings}"

            if len(base) > 1015:
                base = base[:1015]  + " [...]"

            data.append(base)

        return data


    def examples_search(arg: str) -> list:
        request = Sentence.request(arg)

        if not request:
            return [f"No examples found for {arg}."]

        results = json.loads(request.json())
        data = []
        base = ""

        for index, result in enumerate(results["data"], start=1):
            japanese = result["japanese"]
            en_translation = result["en_translation"]
            base += f"{index}. {japanese}\n{en_translation}\n\n"

        if len(base) > 1015:
            base = base[:1015]  + " [...]"

        data.append(base)
        return data


    def token_search(arg: str) -> list:
        request = Tokens.request(arg)

        if not request:
            return [f"No tokens found for {arg}."]

        results = json.loads(request.json())
        data = []
        base = ""

        for token in results["data"]:
            base += f"{token['token']} {token['pos_tag']}\n"

        if len(base) > 1015:
            base = base[:1015]  + " [...]"

        data.append(base)
        return data


async def word(update: Update, context: ContextTypes.DEFAULT_TYPE):
    word = update.message.text
    msg = Jisho.word_search(word)[0]
    chat_id = update.effective_chat.id
    thread_id = update.message.message_thread_id
    await context.bot.send_message(chat_id=chat_id, message_thread_id=thread_id, text=msg + "\n/stop")


async def kanji(update: Update, context: ContextTypes.DEFAULT_TYPE):
    word = update.message.text
    msg = Jisho.kanji_search(word)[0]
    chat_id = update.effective_chat.id
    thread_id = update.message.message_thread_id
    await context.bot.send_message(chat_id=chat_id, message_thread_id=thread_id, text=msg + "\n/stop")


async def examples(update: Update, context: ContextTypes.DEFAULT_TYPE):
    word = update.message.text
    msg = Jisho.examples_search(word)[0]
    chat_id = update.effective_chat.id
    thread_id = update.message.message_thread_id
    await context.bot.send_message(chat_id=chat_id, message_thread_id=thread_id, text=msg + "\n/stop")


async def token(update: Update, context: ContextTypes.DEFAULT_TYPE):
    word = update.message.text
    msg = Jisho.token_search(word)[0]
    chat_id = update.effective_chat.id
    thread_id = update.message.message_thread_id
    await context.bot.send_message(chat_id=chat_id, message_thread_id=thread_id, text=msg + "\n/stop")


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
        [InlineKeyboardButton("All Commands", callback_data="start/help")]])

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
    cmd = query.data.removeprefix("jisho/")

    if cmd == "word":
        await query.answer("Enter word to search...")
        await update.effective_message.edit_text("Enter word to search or /stop:")
        return State.WORD_SEARCH

    if cmd == "kanji":
        await query.answer("Enter kanji to search...")
        await update.effective_message.edit_text("Enter kanji to search or /stop:")
        return State.KANJI_SEARCH
    
    if cmd == "examples":
        await query.answer("Enter word to search examples...")
        await update.effective_message.edit_text("Enter word to search examples for or /stop:")
        return State.EXAMPLES_SEARCH
    
    if cmd == "token":
        await query.answer("Enter sentence to tokenize...")
        await update.effective_message.edit_text("Enter Japanese sentence to tokenize or /stop:")
        return State.TOKEN_SEARCH