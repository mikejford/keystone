DUNGEON_LIST = {
    'De Other Side': ['DOS'],
    'Halls of Atonement': ['HOA', 'Halls'],
    'Mists of Tirna Scithe': ['MOTS', 'Mists'],
    'Plaguefall': ['PF'],
    'Sanguine Depths': ['SD'],
    'Spires of Ascension': ['SOA', 'Spires'],
    'The Necrotic Wake': ['NW'],
    'Theater of Pain': ['TOP', 'Theater'],
}

BFA_DUNGEON_LIST = {
    'Atal\'Dazar': ['AD', 'Atal'],
    'Freehold': ['FH'],
    'King\'s Rest': ['KR'],
    'Shrine of the Storm': ['SOTS', 'SOS', 'Shrine'],
    'Siege of Boralus': ['SB', 'SOB', 'Siege'],
    'Temple of Sethraliss': ['TOS', 'Temple'],
    'The MOTHERLODE!!': ['ML', 'Motherlode'],
    'The Underrot': ['UR', 'Underrot'],
    'Tol Dagor': ['TD', 'Tol'],
    'Waycrest Manor': ['WM', 'Waycrest', 'Manor'],
    'Mechagon Junkyard': ['JY', 'Junkyard'],
    'Mechagon Workshop': ['WS', 'Workshop'],
}

DUNGEON_ABBR_LIST = {}
for name, abbrs in DUNGEON_LIST.items():
    DUNGEON_ABBR_LIST.update(dict.fromkeys([a.lower() for a in abbrs], name))
    DUNGEON_ABBR_LIST.update({name.lower(): name})

MIN_KEYSTONE_LEVEL = 2

GITHUB_URL = 'https://github.com/mikejford/keystone'
GITHUB_ICON_URL = 'https://image.flaticon.com/icons/svg/25/25231.svg'
AFFIX_URL = 'https://raider.io/api/v1/mythic-plus/affixes?region=us&locale=en'
KEYSTONE_ICON_URL = 'https://wow.zamimg.com/images/wow/icons/large/inv_relics_hourglass.jpg'
KEYSAPI_ADD_KEY_URL = 'https://espkrandardsaskunclezar20200801100540.azurewebsites.net/api/keys'
