import re
from peewee import fn

from bot_mattermost_music.decorators import only_admins, started_pool
from bot_mattermost_music.help_functions import create_top, upload_song
from bot_mattermost_music.utils import state
from bot_mattermost_music.songs import Song
from mmpy_bot.bot import listen_to

@listen_to('--help')
def get_help(message):
    help_message = (
        "\n**Admin commands**\n"
        "--disco to start poll\n"
        "--poptop [num] output referenced song (e.g. /poptop or /poptop 5)\n"
        "--finish to end poll\n"
        "--settings_mp3 on|off (e.g. /settings_mp3 or /settings_mp3 on)\n"
        "--poll_status to print status of poll in this chat\n"
        "**User commands**\n"
        "--top [num] output top songs(e.g. /top 5)\n"
        "--vote [num] vote for song from poll (e.g. /vote 5)\n"
    )
    message.reply(help_message)


@listen_to('--disco')
@only_admins
def create_poll(message):
    if state.config["poll_started"]:
        message.reply("\nPrevious poll hasn't finished yet. Type /finish or use pined Message")
    else:
        state.config["poll_started"] = True
        music_poll = '\n'
        for idx, song in enumerate(Song.select().order_by(Song.author).execute()):
            music_poll += f'{idx + 1}. {song.author} | {song.title}\n'
        message.reply(music_poll)


@listen_to('--top')
@started_pool
def get_songs_top_list(message):
    state.config["top_songs"].clear()
    create_top()
    music_poll = '\n'
    try:
        top_number = int(re.search(r'^--top ([\d]*)$', message.get_message()).group(1))
        if top_number == 0:
            raise AttributeError
    except AttributeError:
        message.reply('\nIncorrect input. Type /help to get information about commands')
    else:
        for idx, song in enumerate(state.config["top_songs"][:top_number]):
            music_poll += f'{idx + 1}. {song["author"]} | {song["title"]} | {song["mark"]} Votes\n'
        message.reply(music_poll)


@listen_to('--vote')
@started_pool
def vote_for_song(message):
    try:
        idx = int(re.search(r'^--vote ([\d]*)$', message.get_message()).group(1))
        if idx > state.config["count_music"] or idx < 0:
            raise AttributeError
    except AttributeError:
        reply_message = f'\nNumber should be less than {state.config["count_music"]} and greater than 0'
        message.reply(reply_message)
    else:
        state.config["top_songs"].clear()
        if message.get_user_id() not in Song.get_by_id(idx).voted_users:
            song_item = Song.get_by_id(idx)
            song_item.update(
                mark=song_item.mark + 1
                ).where(Song.id_music == song_item.id_music).execute()
            song_item.update(
                voted_users=fn.array_append(Song.voted_users, str(message.get_user_id()))
                ).where(Song.id_music == song_item.id_music).execute()
        else:
            song_item = Song.get_by_id(idx)
            song_item.update(
                mark=song_item.mark - 1
                ).where(Song.id_music == song_item.id_music).execute()
            song_item.update(
                voted_users=fn.array_remove(Song.voted_users, str(message.get_user_id()))
                ).where(Song.id_music == song_item.id_music).execute()


@listen_to('--poptop')
@only_admins
@started_pool
def pop_element_from_top(message):
    try:
        if message.get_message() == '--poptop':
            idx = 0
        else:
            idx = int(re.search(r'^--poptop ([\d]*)$', message.get_message()).group(1)) - 1
        if idx > state.config["count_music"] or idx < 0:
            raise AttributeError
    except AttributeError:
        reply_message = f'\nNumber should be less than {state.config["count_music"]} and greater than 0'
        message.reply(reply_message)
    else:
        if not state.config["top_songs"]:
            create_top()
        song_item = state.config["top_songs"][idx]
        if state.config["upload_flag"]:
            upload_song(song_item, message, state)
        else:
            bot_reply_message = f'\n{song_item["author"]} | {song_item["title"]}'
            message.reply(bot_reply_message)

        song_index = song_item["pos"]  # positions of songs starts by 1

        song_item = Song.get_by_id(song_index)
        Song.update(voted_users=[]).where(Song.id_music == song_item.id_music).execute()
        Song.update(mark=0).where(Song.id_music == song_item.id_music).execute()
        state.config["top_songs"] = []


@listen_to('--finish')
@only_admins
@started_pool
def finish_poll(message):
    state.config["poll_started"] = False
    Song.truncate_table(restart_identity=True)
    state.save_config()
    state.__init__()
    message.reply("\nPoll was finished")


@listen_to('--settings_mp3')
@only_admins
def change_upload_flag(message):
    if message.get_message() == '--settings_mp3':
        state.config["upload_flag"] = False if state.config["upload_flag"] else True
    else:
        switch = message.get_message().replace('--settings_mp3', '').split()[0]
        if switch == 'on':
            state.config["upload_flag"] = True
        elif switch == 'off':
            state.config["upload_flag"] = False
    bot_message = f'\nUploading songs is **{"Enabled" if state.config["upload_flag"] else "Disabled"}**'
    message.reply(bot_message)


@listen_to('--poll_status')
@only_admins
def get_poll_status(message):
    status = (
        '\nPoll status\n'
        '———————————\n'
        f'Poll started: {state.config["poll_started"]}\n'
        f'Upload mp3: {"on" if state.config["upload_flag"] else "off"}'
    )
    message.reply(status)
