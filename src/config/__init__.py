import os
import logging
from dotenv import load_dotenv; load_dotenv()
from .botsetup import Bot, Event, load_handlers

BOT_TOKEN = os.getenv("BOT_TOKEN")
SPDICT_TOKEN = os.getenv("SPDICT_TOKEN")

bot = Bot(token=BOT_TOKEN)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

load_handlers()