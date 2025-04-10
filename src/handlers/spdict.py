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


def search_word(query):
    r = requests.get(URL + query + KEY).json()[0]
    short_def = ", ".join(r["shortdef"])
    q = query.replace('20%', ' ')
    base = f"Searched for '{q}'.\nMeans: {short_def}"
    return base


def search_conjugation(query, flag: str=""):
    req = requests.get(URL + query + KEY).json()
    for r in req:
        if "suppl" in r:
            conjugations: list[dict] = r["suppl"]["cjts"]
            base = ""
            t = ""

            if "-" in flag:
                try:
                    t = getattr(ConjType, f"{flag.split("-")[1].upper()}")
                except AttributeError as e:
                    print(e)

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

# TODO - need better command names

@bot.command()
async def word(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """English-Spanish dictionary word search"""
    query: str = " ".join(context.args)
    await context.bot.send_message(chat_id=update.effective_chat.id, text=search_word(query))


@bot.command()
async def conjugate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Shows conjugations of spanish verbs. Do '/conjugate help' for flags"""
    if context.args and context.args[0] == "help":
        msg = f"List of conjugation flags (ex. /conjugate <flag> beber):\n{'\n'.join(['-'+i.name.lower() for i in list(ConjType)[1:]])}"
        await context.bot.send_message(chat_id=update.effective_chat.id, text=msg)
        return

    if context.args and "-" in (flag:=context.args[0]):
        query: str = " ".join(context.args[1:])

    else:
        flag: str = ""
        query: str = " ".join(context.args)

    await context.bot.send_message(chat_id=update.effective_chat.id, text=search_conjugation(query, flag=flag))