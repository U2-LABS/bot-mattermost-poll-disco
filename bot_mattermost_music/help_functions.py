import os

from bot_mattermost_music.songs import Song
from bot_mattermost_music.utils import state
from playhouse.shortcuts import model_to_dict

def create_top():
    top_list = Song.select().order_by(Song.mark.desc(), Song.pos)
    for song in top_list:
        state.config["top_songs"].append(model_to_dict(song))


def _download_music_link(music_link, name):
    import requests
    ok_status_code = 200
    link = music_link
    req = requests.get(link, stream=True)
    if req.status_code == ok_status_code:
        with open(name, 'wb') as mp3:
            mp3.write(req.content)


def upload_song(song, message, state):
    song_name = f'{song["author"]} - {song["title"]}.mp3'.replace('/', '|')
    _download_music_link(song["link"], song_name)
    audio = open(song_name, 'rb')
    result = message.upload_file(audio)
    audio.close()
    if 'file_infos' not in result:
        message.reply('upload file error')
    file_id = result['file_infos'][0]['id']
    message.reply('', [file_id])
    os.remove(song_name)
