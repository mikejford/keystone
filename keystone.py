import requests
from tinydb import TinyDB, Query
from datetime import datetime, timedelta
from constants import AFFIX_URL

from keys_api import KeysApi

# remove after tinydb is working
import jsonpickle 
from threading import Lock

lock = Lock()
keys_api = KeysApi()

# remove after tinydb is working
def keystone_insort_right(a, x, lo=0, hi=None):
    if hi is None:
        hi = len(a)

    while lo < hi:
        mid = (lo+hi)//2
        if a[mid].level > x.level:
            lo = mid + 1
        else:
            hi = mid
    a.insert(lo, x)

class Keystone():
    def __init__(self, dungeon, level, name, user_id, invalid_after):
        self.dungeon = dungeon
        self.level = level
        self.owner = name
        self.user_id = user_id
        self.invalid_after = invalid_after

class KeystoneStorage():
    def __init__(self):
        self.db = TinyDB('keystonedb.json')
        self._reset_cache()

        # jsonpickle related operations
        with lock:
            try:
                with open('keystone_cache.json', 'r') as f:
                    cache_data = jsonpickle.decode(f.read())
                    now = datetime.utcnow()
                    for guild_id, keys in cache_data.items():
                        self.guilds[int(guild_id)] = list(filter(lambda k: (k.invalid_after > now), keys))
            except FileNotFoundError:
                print('No cache data found.')

    def _reset_cache(self):
        # Determine next US server reset time (UTC)
        now = datetime.utcnow()
        next_tuesday = now.replace(hour=15, minute=0, second=0, microsecond=0) + timedelta(days=(1-now.weekday()) % 7)
        if now > next_tuesday:
            next_tuesday += timedelta(days=7)
        self.timestamp = next_tuesday

        # Remove expired keys from storage
        key = Query()
        self.db.remove(key.invalid_after.test(KeystoneStorage._test_expired_key, now))

        # Load weekly affixes
        self.load_affixes()

        # jsonpickle related operations
        self.guilds = {}

    def _test_expired_key(val, now):
        # test function used by a query to determine if a key is expired
        return datetime.fromisoformat(val) < now

    # guild_id can be removed with jsonpickle removal
    def check_cache(self, guild_id):
        if datetime.utcnow() > self.timestamp:
            self._reset_cache()
            # jsonpickle related operations
            self._save_cache()
        # jsonpickle related operations
        if guild_id not in self.guilds:
            self.guilds[guild_id] = []

    # jsonpickle related operations
    def _save_cache(self):
        with lock:
            with open('keystone_cache.json', 'w') as f:
                print(jsonpickle.encode(self.guilds), file=f)

    def add_key(self, guild_id, user_id, dungeon, lvl, name):
        self.check_cache(guild_id)
        
        key_dict = {
                'guild_id': guild_id,
                'user_id': user_id,
                'dungeon': dungeon,
                'level': lvl,
                'owner': name,
                'invalid_after': self.timestamp.isoformat()
                }

        key_query = Query()
        added = self.db.upsert(key_dict, (key_query.guild_id == guild_id) & (key_query.owner == name))

        # caller expects a Keystone return value 
        # tinydb upsert returns a list of removed doc ids

        # move this to a separate handler registered with the add command
        # keys_api.post_key(user_id, name, dungeon, lvl)

        # jsonpickle related operations
        key = Keystone(dungeon, lvl, name, user_id, self.timestamp)
        if self.find_key_by_name(guild_id, name) is not None:
            index = self.find_key_by_name(guild_id, name)
            self.guilds[guild_id][index] = key
        else:
            keystone_insort_right(self.guilds[guild_id], key)
        self._save_cache()
        return key

    def remove_key(self, guild_id, user_id, name):
        self.check_cache(guild_id)

        key_query = Query()
        removed = self.db.remove((key_query.guild_id == guild_id) & (key_query.owner == name))

        # caller expects a Keystone return value 
        # tinydb remove returns a list of removed doc ids

        # jsonpickle related operations
        key = None
        index = self.find_key_by_name(guild_id, name)
        if index is not None \
                and user_id == self.guilds[guild_id][index].user_id:
            key = self.guilds[guild_id].pop(index)
        self._save_cache()
        return key

    # jsonpickle related method
    def find_key_by_name(self, guild_id, name):
        for index, keystone in enumerate(self.guilds[guild_id]):
            if keystone.owner == name:
                return index
        return None

    def get_keys_by_guild(self, guild_id):
        # gets the keys by guild sorted by descending level and alphabetical owner name
        key = Query()
        keys = sorted(self.db.search(key.guild_id == guild_id), key=lambda k: k['owner'])
        return sorted(keys, key=lambda k: k['level'], reverse=True)

    def load_affixes(self):
        r = requests.get(AFFIX_URL, timeout=2)
        self.affixes = r.json()
