import os

from dotenv import load_dotenv

from .botsetup import Bot, EntryType, load_handlers, logger
from .buttonmaker import Button

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
SPDICT_TOKEN = os.getenv("SPDICT_TOKEN")

bot = Bot(token=BOT_TOKEN)

load_handlers()