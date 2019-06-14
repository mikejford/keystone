## Keystone

A Discord bot for tracking World of Warcraft mythic+ keystones. Made with the [discord.py](https://github.com/Rapptz/discord.py) library.

## How to Run

1. Go to https://discordapp.com/developers/applications/me
2. Create an application & retrieve your bot token
3. Clone the repo & navigate to directory
4. Run `pipenv install` or run `pip install -r requirements.txt`
5. Create a file named token.txt in the repo directory
6. Put your token in `token.txt`
7. Run `pipenv run python keystone_bot.py` or run `python keystone_bot.py`

## Commands

| Command | Description |
|---------|-------------|
| help | explains how to use the bot|
| dungeons | list of dungeons and acceptable abbreviations |
| add | adds a key |
| remove | removes a key |
| keys | lists current stored keys |
| affixes | lists the weekly affix information |

![](images/bot_example.png)
