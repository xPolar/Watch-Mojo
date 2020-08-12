import asyncio
import datetime
from os import system

import discord
from discord.ext import commands, tasks

import Config

class CommunityAnnouncements(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.community_posts.start()
        self.run_node.start()
    
    def cog_unload(self):
        self.community_posts.cancel()
        self.run_node.cancel()
    
    @tasks.loop(minutes = 15)
    async def run_node(self):
        system(f'node "{Config.PATH_TO_JS_FILE}"')
    
    @tasks.loop(minutes = 1)
    async def community_posts(self):
        while self.bot.is_ready() == False:
            await asyncio.sleep(1)
        documents = list(Config.CLUSTER["youtube"]["community"].find({"posted": False}))
        if documents != []:
            channel = self.bot.get_channel(Config.CHANNEL)
            if channel == None:
                print("[YouTube Notifications] The channel providing in the configuration file does not exist!")
            else:
                for post in documents:
                    embed = discord.Embed(
                        description = post["content"] + f"\n\n[View Post]({post['url']})",
                        color = Config.MAINCOLOR
                    )
                    embed.set_author(name = "WatchMojo.com")
                    message = await channel.send(embed = embed)
                    Config.CLUSTER["youtube"]["community"].update_one({"_id": post["_id"]}, {"$set": {"posted": True, "message": message.id}})

def setup(bot):
    bot.add_cog(CommunityAnnouncements(bot))
