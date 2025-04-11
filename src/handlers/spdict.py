from enum import Enum
import requests
from telegram import Update
from telegram.ext import ContextTypes
from config import bot, SPDICT_TOKEN

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


def word_search(query):
    r = requests.get(URL + query + KEY).json()[0]
    short_def = ", ".join(r["shortdef"])
    q = query.replace('20%', ' ')
    base = f"Searched for '{q}'.\nMeans: {short_def}"
    return base


def conjugate(verb, flag: str=""):
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


@bot.command()
async def spdict(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """English-Spanish dictionary word search"""

    if context.args:
        word: str = " ".join(context.args)
        msg = word_search(word)

    else:
        msg = "Please enter a word to search (ex. '/spdict mesa')"
    
    chat_id = update.effective_chat.id
    thread_id = update.message.message_thread_id
    await context.bot.send_message(chat_id=chat_id, message_thread_id=thread_id, text=msg)


@bot.command()
async def spverb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Shows conjugations of spanish verbs. Do '/spverb help' for flags"""

    if context.args:
        flags = ['-'+cjtype.name.lower() for cjtype in list(ConjType)[1:]]

        first_arg = context.args[0].lower()

        if first_arg == "help":
            msg: str = f"List of conjugation flags (ex. /spverb <flag> beber):\n{'\n'.join(flags)}"

        elif first_arg in flags:
            verb: str = " ".join(context.args[1:])
            msg: str = conjugate(verb, flag=first_arg)

        else:
            verb: str = " ".join(context.args)
            msg: str = conjugate(verb)

    else:
        msg = "Please enter a verb to conjugate (ex. '/spverb caminar')"
    
    chat_id = update.effective_chat.id
    thread_id = update.message.message_thread_id
    await context.bot.send_message(chat_id=chat_id, message_thread_id=thread_id, text=msg)