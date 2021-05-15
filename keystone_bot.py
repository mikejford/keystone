import discord
from discord.ext import commands
from basic_commands import BasicCommands

token = open("token.txt", "r").read().strip()

intents = discord.Intents(messages=True, guilds=True)
bot = commands.Bot(command_prefix=commands.when_mentioned_or('!ks '), intents=intents)

@bot.event
async def on_ready():
    print('Logged in as {0.user}'.format(bot))

bot.add_cog(BasicCommands(bot))
bot.run(token)
