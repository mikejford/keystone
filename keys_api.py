import requests

from constants import KEYSAPI_ADD_KEY_URL, DUNGEON_ABBR_LIST

class KeysApi():

    def post_key(self, user_id, character, dungeon, key_level):
        try:
            postData = {'userId': user_id, 'character': character, 'dungeon': DUNGEON_ABBR_LIST[dungeon], 'keyLevel': key_level }
            response = requests.post(KEYSAPI_ADD_KEY_URL, json = postData, timeout=0.2)
        except requests.Timeout as error:
            # We don't care about waiting for the response, so we are using a very low timeout and ignoring the exception
            pass
        except:
            # We want this to run silently for now so we will suppress any exceptions
            pass
         