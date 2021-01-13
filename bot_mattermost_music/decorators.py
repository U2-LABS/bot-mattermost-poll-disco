import re

from bot_mattermost_music.utils import state


def only_admins(func):
    def check_admin_permissions(message):
        result = re.search(r'system_admin', message.get_user_info('roles'))
        if result:
            func(message)
        else:
            message.reply("You don't have permission")
    return check_admin_permissions


def started_pool(func):
    def check_is_pool_started(message):
        if not state.config["poll_started"]:
            message.reply("Poll hasn't started yet. Type /disco to start")
        else:
            func(message)
    return check_is_pool_started
