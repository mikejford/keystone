import discord
from discord.ext import commands
from basic_commands import BasicCommands

def get_prefix(bot, message):
    prefix = ""
    if not isinstance(message.channel, discord.DMChannel):
        prefix = "!ks "
    return commands.when_mentioned_or(prefix)(bot, message)

# TODO use environment variable (BOT_TOKEN)
token = open("token.txt", "r").read().strip()

intents = discord.Intents(messages=True, guilds=True)

bot = commands.Bot(command_prefix=get_prefix, intents=intents)
bot.add_cog(BasicCommands(bot))

# TODO use environment variable (PLUGINS_ENABLED)
# TODO walk the plugin directory to load extensions
bot.load_extension("plugin.keys_api")

@bot.event
async def on_ready():
    print('Logged in as {0.user}'.format(bot))
    appinfo = await bot.application_info()
    print(repr(appinfo))

bot.run(token)
