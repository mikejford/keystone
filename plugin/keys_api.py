import os
import requests

# Convert the constants into system values maintained in tinydb table
from constants import KEYSAPI_ADD_KEY_URL, DUNGEON_ABBR_LIST

def setup(bot):
    # TODO use environment variable to enable (KEYS_API_ENABLED)
    add_cmd = bot.get_command("add")
    add_cmd.after_invoke(post_key)

async def post_key(_, ctx):
    keystone = ctx.kwargs["key"]
    bot_env = os.getenv("BOT_ENV", "test")

    try:
        postData = {
                'userId': keystone.user_id,
                'character': keystone.owner,
                'dungeon': DUNGEON_ABBR_LIST[keystone.dungeon],
                'keyLevel': keystone.level,
                'environment': bot_env
                }
        response = requests.post(KEYSAPI_ADD_KEY_URL, json = postData, timeout=0.2)
    except requests.Timeout as error:
        # We don't care about waiting for the response, so we are using a very low timeout and ignoring the exception
        pass
    except:
        # We want this to run silently for now so we will suppress any exceptions
        pass
