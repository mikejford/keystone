import discord
from discord.ext import commands
from keystone import Keystone, KeystoneStorage
from constants import DUNGEON_LIST, DUNGEON_ABBR_LIST, KEYSTONE_ICON_URL, SELF_DESTRUCT_MSG_TIMER

token = open("token.txt", "r").read().strip()

name_len = max(map(lambda name: len(name), DUNGEON_LIST.keys()))
abbr_len = max(map(lambda abbrs: len(', '.join(abbrs)), DUNGEON_LIST.values()))

keystones = KeystoneStorage()

bot = commands.Bot(command_prefix='!ks ')

@bot.event
async def on_ready():
    print('Logged in as {0.user}'.format(bot))

@bot.after_invoke
async def cleanup_chat(ctx):
    await ctx.message.delete()

class AddCommandError(commands.CommandError):
    pass

class RemoveCommandError(commands.CommandError):
    pass

def generate_embed(ctx, key: Keystone = None):
    embed = discord.Embed()
    embed.set_author(name='Mythic Keystones', icon_url=KEYSTONE_ICON_URL)

    if ctx.command.name == 'add' \
            and key is not None:
        embed.add_field(name=key.owner, value=' '.join([DUNGEON_ABBR_LIST[key.dungeon], str(key.level)]), inline=False)

        affix_names = []
        for index, affix in enumerate(keystones.affixes['affix_details']):
            if index >= key.level/3:
                break
            affix_names.append(affix['name'])
        embed.add_field(name='Affixes', value=', '.join(affix_names), inline=False)

    if ctx.command.name == 'keys':
        if ctx.guild.id in keystones.guilds \
                and keystones.guilds[ctx.guild.id]: 
            for k in keystones.guilds[ctx.guild.id]:
                embed.add_field(name=k.owner, value=' '.join([DUNGEON_ABBR_LIST[k.dungeon], str(k.level)]), inline=False)
        else:
            embed.add_field(name='No keys have been added.', value='Add a key with the "!ks add" command', inline=False)

    if ctx.command.name == 'affixes':
        for affix in keystones.affixes['affix_details']:
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
    await ctx.send(content='Keystone added by {}'.format(ctx.author.display_name), embed=generate_embed(ctx, key), delete_after=SELF_DESTRUCT_MSG_TIMER)

@add.error
async def add_error(ctx, error):
    if isinstance(error, commands.CommandError):
        await ctx.send(error)

@bot.command(help='Removes your saved keystone from the list', aliases=['rm', 'delete', 'del', '-'])
async def remove(ctx, character: str = None):
    name = character or ctx.author.display_name
    if not keystones.remove_key(ctx.guild.id, ctx.author.id, name):
        raise RemoveCommandError('You are unable to remove that key')
    await ctx.send('Keystone removed by {}'.format(ctx.author.display_name), delete_after=SELF_DESTRUCT_MSG_TIMER)

@remove.error
async def remove_error(ctx, error):
    if isinstance(error, commands.CommandError):
        await ctx.send(error)

@bot.command(help='Lists the stored keystones and weekly affix information', aliases=['list'])
async def keys(ctx):
    keystones.check_cache(ctx.guild.id)
    await ctx.send(content='Current keystone list', embed=generate_embed(ctx), delete_after=SELF_DESTRUCT_MSG_TIMER)

@bot.command(help='Lists the weekly affix information')
async def affixes(ctx):
    keystones.check_cache(ctx.guild.id)
    await ctx.send(embed=generate_embed(ctx), delete_after=SELF_DESTRUCT_MSG_TIMER)

@bot.command(help='Lists the dungeons and acceptable abbreviations')
async def dungeons(ctx):
    header = '| {:<{name_len}} | {:<{abbr_len}} |'.format('Dungeon', 'Abbreviations', name_len=name_len, abbr_len=abbr_len)
    msg = header + '\n' + ('-' * len(header)) + '\n'
    for name, abbr in DUNGEON_LIST.items():
        msg += '| {:<{name_len}} | {:<{abbr_len}} |\n'.format(name, ', '.join(abbr), name_len=name_len, abbr_len=abbr_len)
    await ctx.send('```' + msg + '```', delete_after=SELF_DESTRUCT_MSG_TIMER)

bot.run(token)
