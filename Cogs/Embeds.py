import datetime

import discord
import pymongo
from discord.ext import commands

import Config

class Embeds(commands.Cog):

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
    
    @commands.command()
    async def embed(self, ctx, *, details = None):
        if self.bypass_filter(ctx) == True:
            try:
                await ctx.message.delete()
            except discord.Forbidden:
                pass
            if details == None:
                return
            else:
                if details != None:
                    title = details.split("||")[0]
                    description = False
                    if len(details.split("||")) >= 2:
                        description = details.split("||")[1]
                    embed = discord.Embed(
                        title = title,
                        color = Config.MAINCOLOR
                    )
                    if description != False:
                        embed.description = description
                    if ctx.message.attachments != []:
                        try:
                            embed.set_image(url = ctx.message.attachments[0].url)
                        except:
                            pass
                    await ctx.send(embed = embed)

def setup(bot):
    bot.add_cog(Embeds(bot))
