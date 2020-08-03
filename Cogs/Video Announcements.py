import asyncio
import datetime
import json

import aiohttp
import discord
import pymongo
from discord.ext import commands, tasks

import Config

class VideoAnnouncements(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
    #     self.Check_YouTube.start()

    # def cog_unload(self):
    #     self.Check_YouTube.cancel()

    # @tasks.loop(minutes = 15)
    # async def Check_YouTube(self):
    #     while self.bot.is_ready() == False:
    #         await asyncio.sleep(5)
    #     try:
    #         async with aiohttp.ClientSession() as session:
    #             async with session.get(f"https://www.googleapis.com/youtube/v3/search?key={Config.API_KEY}&channelId=UCaWd5_7JhbQBe4dknZhsHJg&part=snippet,id&order=date&maxResults=2") as resp:
    #                 if resp.status == 200:
    #                     data = await resp.text()
    #                     data = json.loads(data)
    #                     for video in data["items"]:
    #                         print(video)
    #                         # database = Config.CLUSTER["youtube"]["videos"].find_one({"_id": video["id"]["videoId"]})
    #                         # if database == None:
    #                         #     print(video)
    #                         #     async with session.get(f"https://www.googleapis.com/youtube/v3/videos?id={video['id']['videoId']}&key={Config.API_KEY}&part=snippet") as resp:
    #                         #         if resp.status == 200:
    #                         #             data = await resp.text()
    #                         #             data = json.loads(data)
    #                         #     embed = discord.Embed(
    #                         #         title = video["snippet"]["title"],
    #                         #         url = f"https://www.youtube.com/watch?v={video['id']['videoId']}",
    #                         #         description = description,
    #                         #         timestamp = datetime.datetime.strptime(video["snippet"]["publishedAt"], "%Y-%m-%dT%H:%M:%SZ"),
    #                         #         color = 0xFF0000
    #                         #     )
    #                         #     embed.set_author(name = video["snippet"]["channelTitle"], url = f"https://www.youtube.com/channel/{video['snippet']['channelId']}")
    #                         #     embed.set_image(url = video["snippet"]["thumbnails"]["high"]["url"])
    #                         #     embed.set_footer(text = "YouTube", icon_url = "https://www.freepnglogos.com/uploads/youtube-icon-logo-7.png")
    #                         #     channels = Config.CLUSTER["servers"]["youtube"].find({})
    #                         #     for channel1 in channels:
    #                         #         guild = discord.utils.get(self.bot.guilds, id = channel1["_id"])
    #                         #         channel = discord.utils.get(guild.text_channels, id = channel1["channel"])
    #                         #         if "message" in channel1:
    #                         #             if channel1["message"] == "reset":
    #                         #                 await channel.send(embed = embed)
    #                         #             else:
    #                         #                 await channel.send(channel1["message"], embed = embed)
    #                         #         else:
    #                         #             await channel.send(embed = embed)
    #                             # Config.CLUSTER["youtube"]["videos"].insert_one({"_id": video["id"]["videoId"]})
    #                 else:
    #                     print(f"There's been a problem chief: {resp.status}")
    #     except Exception as e:
    #         print(e)

    # @commands.command()
    # @commands.has_permissions(manage_guild = True)
    # async def notification(self, ctx, *, formate = None):
    #     if format == None:


def setup(bot):
    bot.add_cog(VideoAnnouncements(bot))
