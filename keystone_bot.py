import discord
from discord.ext import commands
from keystone import Keystone, KeystoneStorage
from constants import DUNGEON_LIST, DUNGEON_ABBR_LIST, MIN_KEYSTONE_LEVEL, KEYSTONE_ICON_URL, SELF_DESTRUCT_MSG_TIMER

token = open("token.txt", "r").read().strip()

name_len = max(map(lambda name: len(name), DUNGEON_LIST.keys()))
abbr_len = max(map(lambda abbrs: len(', '.join(abbrs)), DUNGEON_LIST.values()))

keystones = KeystoneStorage()

intents = discord.Intents(messages=True, guilds=True)
bot = commands.Bot(command_prefix=commands.when_mentioned_or('!ks '), intents=intents)

@bot.event
async def on_ready():
    print('Logged in as {0.user}'.format(bot))

class AddCommandError(commands.UserInputError):
    def __init__(self, message, arg_string = None, show_cmd_fmt = False):
        add_cmd_fmt = "Expected add command arguments: dungeon level [character]"
        m = message
        if (show_cmd_fmt or arg_string):
            m = "\n".join([message, add_cmd_fmt])
        if (arg_string):
            m = "\n".join([m, "User provided values: {}".format(arg_string)])
        super().__init__(m)

class RemoveCommandError(commands.UserInputError):
    pass

def generate_embed(name, value, embed = None):
    if embed is None:
        embed = discord.Embed()
        embed.set_author(name='Mythic Keystones', icon_url=KEYSTONE_ICON_URL)

    embed.add_field(name=name, value=value, inline=False)
    return embed

@bot.command(help='Adds your keystone to the list', aliases=['replace', '+'])
async def add(ctx, *args):
    _args_string = " ".join(args)
    _args_list = list(args)

    character = None
    try:
        _lvl_or_char = _args_list.pop()
        lvl = int(_lvl_or_char)
    except ValueError:
        character = _lvl_or_char
        try:
            _lvl = _args_list.pop()
            lvl = int(_lvl)
        except Exception:
            raise AddCommandError("Unable to determine keystone level from supplied values.", _args_string)
    except IndexError:
        raise AddCommandError("No keystone information provided.", show_cmd_fmt = True)

    dungeon = " ".join(_args_list)

    if dungeon.lower() not in DUNGEON_ABBR_LIST.keys():
        raise AddCommandError("Dungeon abbreviation `{}` not found. Use `!ks dungeons` to see the list of acceptable names and abbreviations".format(dungeon))
    elif lvl < MIN_KEYSTONE_LEVEL:
        raise AddCommandError("Keystone level `{}` is not valid. Provide a numeric value from {} and higher".format(lvl, MIN_KEYSTONE_LEVEL))

    name = character or ctx.author.display_name
    key = keystones.add_key(ctx.guild.id, ctx.author.id, dungeon.lower(), lvl, name)
    embed = generate_embed(key['owner'], ' '.join([DUNGEON_ABBR_LIST[key['dungeon']], str(key['level'])]))

    affix_names = []
    for index, affix in enumerate(keystones.affixes['affix_details']):
        if index >= key['level']/3:
            break
        affix_names.append(affix['name'])
    embed = generate_embed('Affixes', ', '.join(affix_names), embed)
    await ctx.send(content='Keystone added by {}'.format(ctx.author.display_name), embed=embed)

@add.error
async def add_error(ctx, error):
    if isinstance(error, commands.CommandError):
        await ctx.send(error)

@bot.command(help='Removes your saved keystone from the list', aliases=['rm', 'delete', 'del', '-'])
async def remove(ctx, character: str = None):
    name = character or ctx.author.display_name
    key = keystones.remove_key(ctx.guild.id, ctx.author.id, name)
    if not key:
        raise RemoveCommandError('You are unable to remove that key')

    embed = generate_embed(name, "Keystone removed")
    await ctx.send('Keystone removed by {}'.format(ctx.author.display_name), embed=embed)

@remove.error
async def remove_error(ctx, error):
    if isinstance(error, commands.CommandError):
        await ctx.send(error)

@bot.command(help='Lists the stored keystones and weekly affix information', aliases=['list'])
async def keys(ctx):
    keystones.check_cache()

    embed = None
    keys = keystones.get_keys_by_guild(ctx.guild.id)
    for k in keys:
        embed = generate_embed(k['owner'], ' '.join([DUNGEON_ABBR_LIST[k['dungeon']], str(k['level'])]), embed)
    if len(keys) == 0:
        embed = generate_embed('No keys have been added.', 'Add a key with the "!ks add" command')

    await ctx.send(content='Current keystone list', embed=embed)

@bot.command(help='Lists the weekly affix information')
async def affixes(ctx, force_load: bool = False):
    keystones.check_cache()
    if force_load:
        keystones.load_affixes()

    embed = None
    for affix in keystones.affixes['affix_details']:
        embed = generate_embed(affix['name'], affix['description'], embed)

    await ctx.send(content='Weekly affix details', embed=embed)

@bot.command(help='Lists the dungeons and acceptable abbreviations')
async def dungeons(ctx):
    header = '| {:<{name_len}} | {:<{abbr_len}} |'.format('Dungeon', 'Abbreviations', name_len=name_len, abbr_len=abbr_len)
    msg = header + '\n' + ('-' * len(header)) + '\n'
    for name, abbr in DUNGEON_LIST.items():
        msg += '| {:<{name_len}} | {:<{abbr_len}} |\n'.format(name, ', '.join(abbr), name_len=name_len, abbr_len=abbr_len)
    await ctx.send('```' + msg + '```')

bot.run(token)
