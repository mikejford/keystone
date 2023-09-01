import os

import requests

# Convert the constants into system values maintained in tinydb table
from constants import KEYSAPI_ADD_KEY_URL


def setup(bot):
    # TODO use environment variable to enable (KEYS_API_ENABLED)
    print('Loading ESPK keys api plugin...')
    add_cmd = bot.get_command("add")
    add_cmd.after_invoke(post_key)
    print('Loaded ESPK keys api plugin.')

async def post_key(_, ctx):
    keystone = ctx.kwargs["key"]
    bot_env = os.getenv("BOT_ENV", "test")

    try:
        postData = {
                'userId': keystone.user_id,
                'character': keystone.owner,
                'dungeon': keystone.dungeon,
                'keyLevel': keystone.level,
                'environment': bot_env
                }
        response = requests.post(KEYSAPI_ADD_KEY_URL, json = postData)
        print('ESPK keys api request response code: {0}'.format(response.status_code))
    except requests.Timeout as error:
        print('ESPK keys api request timeout error: {0}'.format(error))
    except Exception as error:
        print('ESPK keys api request failed error: {0}'.format(error))
