import discord
from discord.ext import commands
from keystone import Keystone, KeystoneStorage
from constants import DUNGEON_LIST, DUNGEON_ABBR_LIST, KEYSTONE_ICON_URL

token = open("token.txt", "r").read().strip()

name_len = max(map(lambda name: len(name), DUNGEON_LIST.keys()))
abbr_len = max(map(lambda abbrs: len(', '.join(abbrs)), DUNGEON_LIST.values()))

keystones = KeystoneStorage()

bot = commands.Bot(command_prefix='!ks ')

@bot.event
async def on_ready():
    print('Logged in as {0.user}'.format(bot))

class AddCommandError(commands.CommandError):
    pass

class RemoveCommandError(commands.CommandError):
    pass

def generate_embed(ctx, key: Keystone = None):
    embed = discord.Embed()
    embed.set_author(name='Mythic Keystones', icon_url=KEYSTONE_ICON_URL)

    # can this be less hard coded?
    if ctx.invoked_with in ['keys', 'list'] \
            and ctx.guild.id in keystones.guilds:
        names = []
        dungeons = []
        levels = []

        for k in keystones.guilds[ctx.guild.id]:
            names.append(k.owner)
            dungeons.append(DUNGEON_ABBR_LIST[k.dungeon])
            levels.append(str(k.level))

        embed.add_field(name='Name', value='\n'.join(names))
        embed.add_field(name='Dungeon', value='\n'.join(dungeons))
        embed.add_field(name='Level', value='\n'.join(levels))

    if key is not None:
        embed.add_field(name='Name', value=key.owner)
        embed.add_field(name='Dungeon', value=DUNGEON_ABBR_LIST[key.dungeon])
        embed.add_field(name='Level', value=str(key.level))

    for index, affix in enumerate(keystones.affixes['affix_details']):
        if key is not None and index >= key.level/3:
            break
        embed.add_field(name=affix['name'], value=affix['description'], inline=False)

    return embed

@bot.command(help='Adds your keystone to the list', aliases=['replace', '+'])
async def add(ctx, dungeon: str, lvl: int, character: str = None):
    if dungeon.lower() not in DUNGEON_ABBR_LIST.keys():
        raise AddCommandError('Dungeon abbreviation not found. Use `!ks dungeons` to see the list of acceptable abbreviations')
    elif lvl < 2 or lvl > 25:
        raise AddCommandError('Keystone level is not valid. Provide a value between 2 and 25')

    name = character or ctx.author.display_name
    key = keystones.add_key(ctx.guild.id, ctx.author.id, dungeon.lower(), lvl, name)
    await ctx.send(content='Keystone added by {}'.format(ctx.author.display_name), embed=generate_embed(ctx, key))

@add.error
async def add_error(ctx, error):
    if isinstance(error, commands.CommandError):
        await ctx.send(error)

@bot.command(help='Removes your saved keystone from the list', aliases=['rm', 'delete', 'del', '-'])
async def remove(ctx, character: str = None):
    name = character or ctx.author.display_name
    if not keystones.remove_key(ctx.guild.id, ctx.author.id, name):
        raise RemoveCommandError('You are unable to remove that key')
    await ctx.send('Keystone removed by {}'.format(ctx.author.display_name))

@remove.error
async def remove_error(ctx, error):
    if isinstance(error, commands.CommandError):
        await ctx.send(error)

@bot.command(help='Lists the stored keystones and weekly affix information', aliases=['list'])
async def keys(ctx):
    await ctx.send(embed=generate_embed(ctx))

@bot.command(help='Lists the weekly affix information')
async def affixes(ctx):
    await ctx.send(embed=generate_embed(ctx))

@bot.command(help='Lists the dungeons and acceptable abbreviations')
async def dungeons(ctx):
    header = '| {:<{name_len}} | {:<{abbr_len}} |'.format('Dungeon', 'Abbreviations', name_len=name_len, abbr_len=abbr_len)
    msg = header + '\n' + ('-' * len(header)) + '\n'
    for name, abbr in DUNGEON_LIST.items():
        msg += '| {:<{name_len}} | {:<{abbr_len}} |\n'.format(name, ', '.join(abbr), name_len=name_len, abbr_len=abbr_len)
    await ctx.send('```' + msg + '```')

bot.run(token)
