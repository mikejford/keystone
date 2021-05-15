import re

import requests
from tinydb import TinyDB, Query
from datetime import datetime, timedelta

# Convert the constants into system values maintained in tinydb table
from constants import AFFIX_URL, DUNGEON_ABBR_LIST, MIN_KEYSTONE_LEVEL

# move this to a separate handler registered with the add command
from keys_api import KeysApi
keys_api = KeysApi()

class Keystone():
    def __init__(self, keystone_dict):
        for key in keystone_dict:
            setattr(self, key, keystone_dict[key])

    @classmethod
    async def convert(cls, ctx, argument):
        # argument contains
        #   - dungeon abbreviation | name
        #   - keystone level
        #   - (optional) character name
        arg_format = "^(?i)(?:(?P<dungeon>.*?)\s+)(?P<level>\d+)(?:\s+(?P<owner>\w*))?$"
        argument = argument.strip()

        arg_match = re.fullmatch(arg_format, argument)
        if not arg_match:
            raise Exception("Unable to convert user provided value: `{}`".format(argument))

        keystone_dict = arg_match.groupdict()
        keystone_dict["dungeon"] = keystone_dict["dungeon"].lower()
        if keystone_dict["dungeon"] not in DUNGEON_ABBR_LIST.keys():
            raise Exception("Unable to find dungeon name or abbreviation: `{}`".format(keystone_dict["dungeon"]))

        if int(keystone_dict["level"]) < MIN_KEYSTONE_LEVEL:
            raise Exception("Keystone level must be greater than {}".format(MIN_KEYSTONE_LEVEL))

        if not keystone_dict.get("owner"):
            keystone_dict["owner"] = ctx.author.display_name

        # ctx provides
        #   - guild_id
        #   - user_id
        keystone_dict["guild_id"] = ctx.guild.id
        keystone_dict["user_id"] = ctx.author.id

        return cls(keystone_dict)

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

    def check_cache(self):
        if datetime.utcnow() > self.reset_timestamp:
            self._reset_cache()

    def add_key(self, keystone):
        self.check_cache()

        key_dict = vars(keystone)
        key_dict["invalid_after"] = self.reset_timestamp.isoformat()

        key = Query()
        added = self.db.upsert(key_dict, (key.guild_id == keystone.guild_id) & (key.owner == keystone.owner))

        if len(added) == 0:
            raise Exception("Keystone was not saved. Please try again.")

        # move this to a separate handler registered with the add command
        # keys_api.post_key(user_id, name, dungeon, lvl)

        return Keystone(self.db.get(doc_id=added[0]))

    def remove_key(self, guild_id, user_id, name):
        self.check_cache()

        key = Query()
        removed = self.db.remove((key.guild_id == guild_id) & (key.user_id == user_id) & (key.owner == name))

        if len(removed) == 0:
            raise Exception("Keystone was not removed. Please try again.")

        return removed

    # TODO: Change the response to return a list of Keystone objects
    def get_keys_by_guild(self, guild_id):
        # gets the keys by guild sorted by descending level and alphabetical owner name
        key = Query()
        keys = sorted(self.db.search(key.guild_id == guild_id), key=lambda k: k['owner'])
        return sorted(keys, key=lambda k: k['level'], reverse=True)

    def load_affixes(self):
        r = requests.get(AFFIX_URL, timeout=2)
        self.affixes = r.json()
