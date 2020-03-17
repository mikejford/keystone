import requests
import jsonpickle
from datetime import datetime, timedelta
from threading import Lock
from constants import AFFIX_URL

lock = Lock()

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
        self._reset_cache()
        with lock:
            try:
                with open('keystone_cache.json', 'r') as f:
                    cache_data = jsonpickle.decode(f.read())
                    now = datetime.utcnow()
                    for guild_id, keys in cache_data.items():
                        self.guilds[int(guild_id)] = list(filter(lambda k: (k.invalid_after > now), keys))
            except FileNotFoundError:
                print('No cache data found.')

    def find_key_by_name(self, guild_id, name):
        for index, keystone in enumerate(self.guilds[guild_id]):
            if keystone.owner == name:
                return index
        return None

    def _reset_cache(self):
        self.load_affixes()
        self.guilds = {}
        now = datetime.utcnow()
        next_tuesday = now.replace(hour=15, minute=0, second=0, microsecond=0) + timedelta(days=(1-now.weekday()) % 7)
        if now > next_tuesday:
            next_tuesday += timedelta(days=7)
        self.timestamp = next_tuesday

    def check_cache(self, guild_id):
        if datetime.utcnow() > self.timestamp:
            self._reset_cache()
            self._save_cache()
        if guild_id not in self.guilds:
            self.guilds[guild_id] = []

    def _save_cache(self):
        with lock:
            with open('keystone_cache.json', 'w') as f:
                print(jsonpickle.encode(self.guilds), file=f)

    def add_key(self, guild_id, user_id, dungeon, lvl, name):
        self.check_cache(guild_id)
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
        key = None

        index = self.find_key_by_name(guild_id, name)
        if index is not None \
                and user_id == self.guilds[guild_id][index].user_id:
            key = self.guilds[guild_id].pop(index)
        self._save_cache()
        return key

    def load_affixes(self):
        r = requests.get(AFFIX_URL, timeout=2)
        self.affixes = r.json()
