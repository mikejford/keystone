import discord
from discord.ext import commands

# Convert the constants into system values maintained in tinydb table
from constants import KEYSTONE_ICON_URL
from keystone import Keystone, KeystoneException, KeystoneStorage


# TODO Utilities module candidate
def generate_embed(name, value, embed=None):
    if embed is None:
        embed = discord.Embed()
        embed.set_author(name="Mythic Keystones", icon_url=KEYSTONE_ICON_URL)

    embed.add_field(name=name, value=value, inline=False)
    return embed

class BasicCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.keystones = KeystoneStorage()

    @commands.command(help="Adds your keystone to the list",
            aliases=["replace"])
    async def add(self, ctx, *, key: Keystone):
        try:
            key = self.keystones.add_key(key)
        except KeystoneException as e:
            raise commands.CommandError(message=e.message)

        embed = generate_embed(key.owner, ' '.join([key.dungeon, str(key.level)]))
        affix_names = []
        for index, affix in enumerate(self.keystones.affixes["affix_details"]):
            if index >= int(key.level)/3:
                break
            affix_names.append(affix["name"])
        embed = generate_embed("Affixes", ', '.join(affix_names), embed)
        await ctx.send(content="Keystone added by {}".format(ctx.author.display_name), embed=embed)
 
    @add.error
    async def add_command_error(self, ctx, error):
        if isinstance(error, commands.ConversionError):
            await ctx.send(error.original)
        elif isinstance(error, commands.CommandError):
            await ctx.send(error)

    @commands.command(help="Removes your keystone from the list",
            aliases=["delete", "del", "rm"])
    async def remove(self, ctx, character: str=None):
        name = character or ctx.author.display_name

        try:
            key = self.keystones.remove_key(ctx.author.id, name)
        except KeystoneException as e:
            raise commands.CommandError(message=e.message)

        embed = generate_embed(name, "Keystone removed")
        await ctx.send(content="Keystone removed by {}".format(ctx.author.display_name), embed=embed)

    @remove.error
    async def remove_command_error(self, ctx, error):
        if isinstance(error, commands.CommandError):
            await ctx.send(error)

    @commands.command(help="Lists the stored keystones",
            aliases=["keys"])
    async def list(self, ctx):
        self.keystones.check_cache()

        embed = None
        keys = self.keystones.get_keys()
        for k in keys:
            embed = generate_embed(k.owner, ' '.join([k.dungeon, str(k.level)]), embed)
        if len(keys) == 0:
            embed = generate_embed("No keys have been added.", "Add a key with the 'add' command")

        await ctx.send(content="Current Keystones List", embed=embed)

    @commands.command(help="Lists the weekly affix details")
    async def affixes(self, ctx, force_reload: bool = None):
        self.keystones.check_cache()
        if force_reload:
            self.keystones.load_affixes()

        embed = None
        for affix in self.keystones.affixes["affix_details"]:
            embed = generate_embed(affix["name"], affix["description"], embed)

        await ctx.send(content="Weekly Affix Details", embed=embed)

    @commands.command(help="Lists the dungeons and acceptable abbreviations")
    async def dungeons(self, ctx):
        embed = None
        dungeon_list = Keystone.dungeon_list()
        for name, abbr in dungeon_list.items():
            embed = generate_embed(name, abbr, embed)

        await ctx.send(content="Dungeons and Abbreviations", embed=embed)
