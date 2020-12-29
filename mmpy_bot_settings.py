import os

from dotenv import load_dotenv

load_dotenv()

DEBUG = False

BOT_URL = os.getenv("BOT_URL")
BOT_TEAM = os.getenv("BOT_TEAM")
BOT_TOKEN = os.getenv("BOT_TOKEN")

SSL_VERIFY = False

DEFAULT_REPLY_MODULE = 'my_default_reply'