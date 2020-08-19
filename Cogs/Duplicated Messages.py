import datetime

import discord
import pymongo
from discord.ext import commands

import Config

class DuplicatedMessages(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
    
    def bypass_filter(self, ctx):
        if ctx.guild == None:
            return False
        else:
            if ctx.author.id in Config.OWNER_IDS or ctx.author.guild_permissions.manage_guild == True:
                return True
            else:
                document = Config.CLUSTER["servers"]["permissions"].find_one({"_id": ctx.guild.id})
                if document == None:
                    return False
                else:
                    for role in ctx.author.roles:
                        if role.id in document["roles"]:
                            return True
    
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot == False and message.guild != None and self.bypass_filter(message) == False:
            messages = await message.channel.history(limit = 11).flatten()
            if messages[0].author.id == self.bot.user.id:
                messages.pop(1)
            messages.pop(0)
            if message.content != "":
                for m in messages:
                    if m.content.lower() == message.content.lower():
                        try:
                            await message.delete()
                        except discord.NotFound:
                            pass
                        return
            if message.attachments != []:
                for attachment in message.attachments:
                    bytes1 = await attachment.read()
                    for m in messages:
                        if m.attachments != []:
                            for attachment2 in m.attachments:
                                bytes2 = await attachment2.read()
                                if bytes1 == bytes2:
                                    try:
                                        await message.delete()
                                    except:
                                        return
                                    else:
                                        return
                                    return

def setup(bot):
    bot.add_cog(DuplicatedMessages(bot))
