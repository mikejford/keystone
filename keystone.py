import re

import requests
from tinydb import TinyDB, Query
from datetime import datetime, timedelta

# Convert the constants into system values maintained in tinydb table
from constants import AFFIX_URL, DUNGEON_ABBR_LIST, MIN_KEYSTONE_LEVEL

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
            raise KeystoneException("Unable to convert user provided value into a keystone: `{}`".format(argument), conversion_failure=True)

        keystone_dict = arg_match.groupdict()
        keystone_dict["dungeon"] = keystone_dict["dungeon"].lower()
        if keystone_dict["dungeon"] not in DUNGEON_ABBR_LIST.keys():
            raise KeystoneException("Unable to find dungeon name or abbreviation: `{}`\nUse the `dungeons` command to see valid abbreviations".format(keystone_dict["dungeon"]), conversion_failure=True)

        if int(keystone_dict["level"]) < MIN_KEYSTONE_LEVEL:
            raise KeystoneException("Keystone level must be greater than {}".format(MIN_KEYSTONE_LEVEL), conversion_failure=True)

        # ctx provides
        #   - user_id
        #   - author.display_name
        keystone_dict["user_id"] = ctx.author.id

        if not keystone_dict.get("owner"):
            keystone_dict["owner"] = ctx.author.display_name

        return cls(keystone_dict)

class KeystoneException(Exception):
    def __init__(self, msg=None, conversion_failure=False):
        add_cmd_fmt = "Expected command arguments: `dungeon level [character]`"
        if msg is None:
            msg = "An unexpected error occurred."
        if conversion_failure:
            msg = "\n".join([add_cmd_fmt, msg])

        super(KeystoneException, self).__init__(msg)

    @property
    def message(self):
        return str(self)

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

    def load_affixes(self):
        r = requests.get(AFFIX_URL, timeout=2)
        self.affixes = r.json()

    def add_key(self, keystone):
        self.check_cache()

        key_dict = vars(keystone)
        key_dict["invalid_after"] = self.reset_timestamp.isoformat()

        key = Query()
        added = self.db.upsert(key_dict, (key.user_id == keystone.user_id) & (key.owner == keystone.owner))

        if len(added) == 0:
            raise KeystoneException("Keystone was not saved. Please try again.")

        return Keystone(self.db.get(doc_id=added[0]))

    def remove_key(self, user_id, name):
        self.check_cache()

        key = Query()
        key_query = ((key.user_id == user_id) & (key.owner == name))
        found = self.db.search(key_query)

        if len(found) == 0:
            raise KeystoneException("No keystone was found for removal.")

        removed = self.db.remove(key_query)

        if len(removed) == 0:
            raise KeystoneException("Keystone was not removed. Please try again.")

        return removed

    def get_keys(self):
        # gets the keys sorted by descending level and alphabetical owner name
        keys = sorted(self.db.all(), key=lambda k: k["owner"])
        return [Keystone(ks) for ks in sorted(keys, key=lambda k: int(k["level"]), reverse=True)]
