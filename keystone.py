import requests
from tinydb import TinyDB, Query
from datetime import datetime, timedelta
from constants import AFFIX_URL

# move this to a separate handler registered with the add command
from keys_api import KeysApi
keys_api = KeysApi()

# TBD (add json serializer or just use dict)
class Keystone():
    def __init__(self, dungeon, level, name, guild_id, user_id, invalid_after):
        self.dungeon = dungeon
        self.level = level
        self.owner = name
        self.user_id = user_id
        self.guild_id = guild_id
        self.invalid_after = invalid_after

class KeystoneStorage():
    def __init__(self):
        self.db = TinyDB('keystonedb.json')
        self._reset_cache()

    def _reset_cache(self):
        # Determine next US server reset time (UTC)
        now = datetime.utcnow()
        next_tuesday = now.replace(hour=15, minute=0, second=0, microsecond=0) + timedelta(days=(1-now.weekday()) % 7)
        if now > next_tuesday:
            next_tuesday += timedelta(days=7)
        self.reset_timestamp = next_tuesday

        # Remove expired keys from storage
        key = Query()
        self.db.remove(key.invalid_after.test(KeystoneStorage._test_expired_key, now))

        # Load weekly affixes
        self.load_affixes()

    def _test_expired_key(val, now):
        # test function used by a query to determine if a key is expired
        return datetime.fromisoformat(val) < now

    # guild_id can be removed with jsonpickle removal
    def check_cache(self):
        if datetime.utcnow() > self.reset_timestamp:
            self._reset_cache()

    def add_key(self, guild_id, user_id, dungeon, lvl, name):
        self.check_cache()

        key_dict = {
                'guild_id': guild_id,
                'user_id': user_id,
                'dungeon': dungeon,
                'level': lvl,
                'owner': name,
                'invalid_after': self.reset_timestamp.isoformat()
                }

        key = Query()
        added = self.db.upsert(key_dict, (key.guild_id == guild_id) & (key.owner == name))

        # move this to a separate handler registered with the add command
        # keys_api.post_key(user_id, name, dungeon, lvl)

        # caller expects a Keystone return value 
        # tinydb upsert returns a list of changed doc ids
        return self.db.get(doc_id=added[0])

    def remove_key(self, guild_id, user_id, name):
        self.check_cache()

        key = Query()
        removed = self.db.remove((key.guild_id == guild_id) & (key.user_id == user_id) & (key.owner == name))

        # caller expects a Keystone return value 
        # tinydb remove returns a list of removed doc ids
        # unable to get the document after removal
        return removed

    def get_keys_by_guild(self, guild_id):
        # gets the keys by guild sorted by descending level and alphabetical owner name
        key = Query()
        keys = sorted(self.db.search(key.guild_id == guild_id), key=lambda k: k['owner'])
        return sorted(keys, key=lambda k: k['level'], reverse=True)

    def load_affixes(self):
        r = requests.get(AFFIX_URL, timeout=2)
        self.affixes = r.json()
