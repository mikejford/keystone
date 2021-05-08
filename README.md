## Keystone

A Discord bot for tracking World of Warcraft mythic+ keystones. Made with the [discord.py](https://github.com/Rapptz/discord.py) library.

## How to Run

1. Go to https://discordapp.com/developers/applications/me
2. Create an application & retrieve your bot token
3. Clone the repo & navigate to directory
4. (Optional) Run `python -m venv env` to create a virtual python environment
5. (Optional) Run `source env/bin/activate` to activate the virtual python environment
6. Run `pip install -r requirements.txt` to install the required python modules
7. Create a file named token.txt in the repo directory
8. Put your bot token in `token.txt`
9. Run `python keystone_bot.py` to start the keystone bot

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
