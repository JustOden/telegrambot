import requests
from enum import Enum, auto

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, filters, ConversationHandler, CommandHandler, MessageHandler

from config import bot, SPDICT_TOKEN, EntryType

URL = "https://dictionaryapi.com/api/v3/references/spanish/json/"
KEY = f"?key={SPDICT_TOKEN}"


class ConjType(Enum):
    PARTICIPLES = "gppt"
    PRESENT_INDICATIVE = "pind"
    PRETERITE_INDICATIVE = "pprf"
    IMPERFECT_INDICATIVE = "pret"
    FUTURE_INDICATIVE = "futr"
    CONDITIONAL_INDICATIVE = "cond"
    PRESENT_SUBJUNCTIVE = "psub"
    IMPERFECT_SUBJUNCTIVE1 = "pisb1"
    IMPERFECT_SUBJUNCTIVE2 = "pisb2"
    FUTURE_SUBJUNCTIVE = "fsub"
    PRESENT_PERFECT = "ppci"
    PAST_PERFECT = "ppsi"
    PRETERITE_PERFECT = "pant"
    FUTURE_PERFECT = "fpin"
    CONDITIONAL_PERFECT = "cpef"
    PRESENT_PERFECT_SUBJUNCTIVE = "ppfs"
    PAST_PERFECT_SUBJUNCTIVE1 = "ppss1"
    PAST_PERFECT_SUBJUNCTIVE2 = "ppss2"
    FUTURE_PERFECT_SUBJUNCTIVE = "fpsb"
    AFFIRMATIVE_IMPERATIVE = "impf"


class Pronoun(Enum):
    FIRST_PERSON = "yo"
    SECOND_PERSON = "tú"
    THIRD_PERSON = "él/ella/Ud."
    FIRST_PERSON_PLURAL = "nosotros"
    SECOND_PERSON_PLURAL_SPAIN = "vosotros"
    SECOND_PERSON_PLURAL = "ellos/ellas/Uds."


class State(Enum):
    WORD_SEARCH = auto()
    CONJUGATE = auto()


class Spdict:
    def word_search(query):
        r = requests.get(URL + query + KEY).json()[0]
        short_def = ", ".join(r["shortdef"])
        q = query.replace('20%', ' ')
        base = f"Searched for '{q}'.\nMeans: {short_def}"
        return base

    def conjugate_verb(verb, flag: str=""):
        req: list[dict] = requests.get(URL + verb + KEY).json()
        for r in req:
            if "suppl" in r:
                conjugations: list[dict] = r["suppl"]["cjts"]
                base: str = ""
                t: ConjType | str = getattr(ConjType, f"{flag[1:].upper()}") if flag else ""
                for cjt in conjugations:
                    cjtype = ConjType(cjt["cjid"])
                    if cjtype == ConjType.PARTICIPLES:
                        continue
                    if t and cjtype != t:
                        continue
                    base += f"{cjtype.name.replace("_", " ")}\n"
                    for pronoun, conj in zip(list(Pronoun), cjt["cjfs"]):
                        base += f"{pronoun.value} {conj}\n"
                    base += "\n"
                return base


async def word(update: Update, context: ContextTypes.DEFAULT_TYPE):
    word = update.message.text
    msg = Spdict.word_search(word)
    chat_id = update.effective_chat.id
    thread_id = update.message.message_thread_id
    await context.bot.send_message(chat_id=chat_id, message_thread_id=thread_id, text=msg + "\n/stop")


async def verb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    word = update.message.text

    flags = ['-'+cjtype.name.lower() for cjtype in list(ConjType)[1:]]

    first_arg = word.split()[0]

    if first_arg == "help":
        msg: str = f"List of conjugation flags (ex. /spverb <flag> beber):\n{'\n'.join(flags)}"
        chat_id = update.effective_chat.id
        thread_id = update.message.message_thread_id
        await context.bot.send_message(chat_id=chat_id, message_thread_id=thread_id, text=msg + "\n/stop")
        return State.CONJUGATE

    if first_arg in flags:
        verb: str = word[len(first_arg)+1:]
        msg: str = Spdict.conjugate_verb(verb, flag=first_arg)

    else:
        verb: str = word
        msg: str = Spdict.conjugate_verb(verb)

    chat_id = update.effective_chat.id
    thread_id = update.message.message_thread_id
    await context.bot.send_message(chat_id=chat_id, message_thread_id=thread_id, text=msg + "\n/stop")


async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.effective_chat.send_message("Stopped listening for words... returning to /spdict")
    await spdict_command(update, context)
    return ConversationHandler.END


@bot.command_handler(command_name="spdict")
async def spdict_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """English-Spanish dictionary"""

    if len(context.args) > 1:
        if context.args[0].lower() == "word":
            word = " ".join(context.args[1:])
            msg = Spdict.word_search(word)
            await update.effective_chat.send_message(msg)
        
        if context.args[0].lower() == "conjugate":
            word = " ".join(context.args[1:])
            arg = context.args[1:]
            
            flags = ['-'+cjtype.name.lower() for cjtype in list(ConjType)[1:]]

            first_arg = arg[0]

            if first_arg == "help":
                msg: str = f"List of conjugation flags:\n{'\n'.join(flags)}"
                await update.effective_chat.send_message(msg)

            if first_arg in flags:
                verb: str = word[len(first_arg)+1:]
                msg: str = Spdict.conjugate_verb(verb, flag=first_arg)

            else:
                verb: str = word
                msg: str = Spdict.conjugate_verb(verb)
            await update.effective_chat.send_message(msg)

    else:
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