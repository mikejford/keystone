DUNGEON_LIST = {
    'Tazavesh: Streets of Wonder': ['SOW', 'TSW', 'Streets'],
    'Tazavesh: So\'leah\'s Gambit': ['SG', 'TSG', 'Gambit'],
    'Mechagon Junkyard': ['JY', 'Junkyard'],
    'Mechagon Workshop': ['WS', 'Workshop'],
    'Lower Karazhan': ['LKARA', 'LK', 'Lower'],
    'Upper Karazhan': ['UKARA', 'UK', 'Upper'],
    'Grimrail Depot': ['GD', 'GRD', 'Depot'],
    'Iron Docks': ['ID', 'Docks'],
}

DUNGEON_ABBR_LIST = {}
for name, abbrs in DUNGEON_LIST.items():
    DUNGEON_ABBR_LIST.update(dict.fromkeys([a.lower() for a in abbrs], name))
    DUNGEON_ABBR_LIST.update({name.lower(): name})

MIN_KEYSTONE_LEVEL = 2

GITHUB_URL = 'https://github.com/mikejford/keystone'
GITHUB_ICON_URL = 'https://image.flaticon.com/icons/svg/25/25231.svg'
AFFIX_URL = 'https://raider.io/api/v1/mythic-plus/affixes?region=us&locale=en'
KEYSTONE_ICON_URL = 'https://wow.zamimg.com/images/wow/icons/large/inv_relics_hourglass_02.jpg'
KEYSAPI_ADD_KEY_URL = 'https://espkrandardsaskunclezar20200801100540.azurewebsites.net/api/keys'
