import os
import random
import asyncio
from pathlib import Path
from logging import getLogger, DEBUG, StreamHandler, Formatter

import discord
from discord.ext import commands


class Music(commands.Cog):
    def __init__(self, bot, directory):
        self.bot = bot
        self.logger = getLogger(__name__)
        self.volume = 100
        self.directory = directory


    @commands.command()
    async def join(self, ctx, *, channel: discord.VoiceChannel):
        """Joins a voice channel"""
        self.logger.info("exec: join {} {}".format(ctx.message.guild.name, channel))

        if ctx.voice_client is not None:
            return await ctx.voice_client.move_to(channel)

        await channel.connect()

    @commands.command()
    async def list(self, ctx):
        """Get voice list"""
        self.logger.info("exec: list")

        filelist = [x.name for x in self.directory.glob("*")]
        return await ctx.send("\n".join(filelist))

    @commands.command()
    async def play(self, ctx, *, query):
        """Plays a file from the local filesystem"""
        self.logger.info(f"exec: play {query}")
        filelist = [str(x) for x in self.directory.glob(f"*{query}*.*")]
        self.logger.debug(f"filelist: {filelist}")

        if not filelist:
            return await ctx.send(f"File not found: {query}")

        path = random.choice(filelist)

        source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(path))
        ctx.voice_client.play(source, after=lambda e: print('Player error: %s' % e) if e else None)
        ctx.voice_client.source.volume = self.volume / 100

        self.logger.info(f"Now playing: {path}")

    @commands.command()
    async def volume(self, ctx, volume: int):
        """Changes the player's volume"""
        self.logger.info(f"exec: volume {volume}")

        if volume < 0 or 100 < volume:
            return await ctx.send("Please set 0..100")
        self.volume = volume

        if ctx.voice_client is not None and ctx.voice_client.is_playing():
            ctx.voice_client.source.volume = self.volume / 100

        await ctx.send("Changed volume to {}%".format(volume))

    @commands.command()
    async def stop(self, ctx):
        """Stops and disconnects the bot from voice"""

        if not ctx.voice_client is None:
            await ctx.voice_client.disconnect()

    @play.before_invoke
    async def ensure_voice(self, ctx):
        if ctx.voice_client is None:
            self.logger.debug(f"{ctx.author} conneted voice channel: {ctx.author.voice}")
            if ctx.author.voice:
                await ctx.author.voice.channel.connect()
            else:
                msg = f"{ctx.author} are not connected to a voice channel"
                self.logger.debug(msg)
                await ctx.send(msg)
                raise commands.CommandError(msg)
        elif ctx.voice_client.is_playing():
            self.logger.debug("stop playing file")
            ctx.voice_client.stop()


if __name__ == "__main__":
    loglevel = os.environ.get("DISCORDBOT_LOGLEVEL", "INFO")
    token = os.environ.get("DISCORDBOT_TOKEN")
    command_prefix = os.environ.get("DISCORDBOT_COMMAND_PREFIX", "!")
    music_directory = Path(__file__).parent.resolve() / os.environ.get("DISCORDBOT_DIRECTORY", "music")

    logger = getLogger(__name__)
    logger.setLevel(loglevel)

    handler = StreamHandler()
    handler.setLevel(DEBUG)
    handler.setFormatter(Formatter("%(asctime)s %(filename)s:%(lineno)d [%(levelname)s] %(message)s"))
    logger.addHandler(handler)


    bot = commands.Bot(command_prefix=commands.when_mentioned_or(command_prefix))
    logger.info(f"-"*40)
    logger.info(f"log level: {loglevel}")
    logger.info(f"command prefix: {command_prefix}")
    logger.info(f"music directory: {music_directory}")
    logger.info(f"-"*40)

    @bot.event
    async def on_ready():
        logger.info(f"logged in as {bot.user} ({bot.user.id})")

    bot.add_cog(Music(
        bot,
        music_directory,
    ))
    bot.run(token)
