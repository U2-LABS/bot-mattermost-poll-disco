from bot_mattermost_music.handlers import state
from mmpy_bot.bot import Bot

if __name__ == "__main__":
    with state:
        Bot().run()
