import discord
from discord.ext import commands
from constants import DUNGEON_LIST

token = open("token.txt", "r").read().strip()

name_len = max(map(lambda name: len(name), DUNGEON_LIST.keys()))
abbr_len = max(map(lambda abbrs: len(', '.join(abbrs)), DUNGEON_LIST.values()))

dungeon_abbr_list = {}
for name, abbrs in DUNGEON_LIST.items():
    dungeon_abbr_list.update(dict.fromkeys([a.lower() for a in abbrs], name))
print(repr(dungeon_abbr_list))

class InvalidDungeon(commands.CheckFailure):
    pass

bot = commands.Bot(command_prefix='!ks ')

@bot.event
async def on_ready():
    print('Logged in as {0.user}'.format(bot))

@bot.command(help='Adds your keystone to the list', aliases=['replace', '+'])
async def add(ctx, dungeon: str, lvl: int, character: str = None):
    if dungeon.lower() not in dungeon_abbr_list.keys():
        raise InvalidDungeon('Dungeon abbreviation not found. Use `!ks list` to see the list of acceptable abbreviations')

    name = character or ctx.author.display_name
    # ctx.invoked_with reveals how the command was called
    await ctx.send('{} {} added for {}'.format(dungeon, lvl, name))

@add.error
async def add_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        await ctx.send(error)

@bot.command(help='Removes your saved keystone from the list', aliases=['del', '-'])
async def remove(ctx, character: str = None):
    name = character or ctx.author.display_name
    await ctx.send('{} removed their key'.format(name))

@bot.command(help='', aliases=['keys', 'all'])
async def list(ctx):
    await ctx.send('List of keystones')

@bot.command(help='Shows a list of dungeons and acceptable abbreviations')
async def dungeons(ctx):
    header = '| {:<{name_len}} | {:<{abbr_len}} |'.format('Dungeon', 'Abbreviations', name_len=name_len, abbr_len=abbr_len)
    msg = header + '\n' + ('-' * len(header)) + '\n'
    for name, abbr in DUNGEON_LIST.items():
        msg += '| {:<{name_len}} | {:<{abbr_len}} |\n'.format(name, ', '.join(abbr), name_len=name_len, abbr_len=abbr_len)
    await ctx.send('```' + msg + '```')

bot.run(token)
