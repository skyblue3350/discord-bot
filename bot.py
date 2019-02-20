import os

import discord
from discord.ext import commands


extensions = [
    "embed",
]

bot = commands.Bot(command_prefix="/")
for e in extensions:
    bot.load_extension(e)
bot.run(os.environ.get("DISCORD_TOKEN"))

