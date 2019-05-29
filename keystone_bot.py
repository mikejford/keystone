import discord
from discord.ext import commands

token = open("token.txt", "r").read().strip()

bot = commands.Bot(command_prefix='!')

@bot.event
async def on_ready():
    print('Logged in as {0.user}'.format(bot))

@bot.command()
async def add(ctx, dungeon: str, lvl: int, character=None):
    name = character or ctx.author.display_name
    await ctx.send('{} {} added for {}'.format(dungeon, lvl, name))

bot.run(token)
