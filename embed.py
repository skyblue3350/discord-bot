import re

import discord


DISCORD_URLS = re.compile(
    "https://discordapp.com/channels/"
    r"(?P<server>[\d]{18})/(?P<channel>[\d]{18})/(?P<msg>[\d]{18})"
)

class EmbedMessage:
    def __init__(self, bot):
        self.bot = bot

    async def on_ready(self):
        pass

    async def on_message(self, message):
        if message.author == self.bot.user:
            return
        for m in DISCORD_URLS.finditer(message.content):
            if message.guild.id == int(m.group("server")):
                channel = message.guild.get_channel(m.group("channel"))
                msg = await message.channel.get_message(m.group("msg"))

                embed = self.compose_embed(channel, msg)
                await message.channel.send(embed=embed)

    def compose_embed(self, channel, msg):
        embed = discord.Embed(
            description=msg.content,
            timestamp=msg.created_at)
        embed.set_author(
            name=msg.author.display_name,
            icon_url=msg.author.avatar_url)
        embed.set_footer(text="via #{name}".format(name=msg.channel.name))
        return embed

def setup(bot):
    bot.add_cog(EmbedMessage(bot))
