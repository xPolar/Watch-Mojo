import re

import discord
import pymongo
from discord.ext import commands

import Config

class BlacklistingWords(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
    
    def cog_check(self, ctx):
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
    
    @commands.group()
    async def blacklistedwords(self, ctx):
        if ctx.invoked_subcommand == None:
            return
    
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot == False and message.guild != None and self.bypass_filter(message) == False:
            document = Config.CLUSTER["servers"]["blacklistedwords"].find_one({"_id": message.guild.id})
            if document != None:
                for word in document["words"]:
                    in_messsage = re.search(f"\\b{word}\\b", message.content.lower())
                    if in_messsage != None:
                        try:
                            await message.delete()
                            return
                        except:
                            return
    
    @blacklistedwords.command()
    async def list(self, ctx):
        try:
            await ctx.message.delete()
        except discord.Forbidden:
            pass
        document = Config.CLUSTER["servers"]["blacklistedwords"].find_one({"_id": ctx.guild.id})
        if document == None:
                return
        else:
            if document["words"] == []:
                embed = discord.Embed(
                    title = f"Blacklisted Words List",
                    description = "There are currently no blacklisted words in this server!",
                    color = Config.MAINCOLOR
                )
            else:
                words = []
                for word in document["words"]:
                    words.append(f"`{word}`")
                words[-1] = f"and {words[-1]}" if len(words) > 1 else words[-1]
                embed = discord.Embed(
                    title = f"Blacklisted Words List",
                    description = ", ".join(words) + ".",
                    color = Config.MAINCOLOR
                )
        await ctx.send(embed = embed)
    
    @blacklistedwords.command()
    async def add(self, ctx, *, words = None):
        try:
            await ctx.message.delete()
        except discord.Forbidden:
            pass
        if words == None:
            return
        else:
            document = Config.CLUSTER["servers"]["blacklistedwords"].find_one({"_id": ctx.guild.id})
            if document == None:
                embed = discord.Embed(
                    title = "Blacklisted Words Updated!",
                    description = f"{words} has been added to the blacklisted words list!!",
                    color = Config.MAINCOLOR
                )
                Config.CLUSTER["servers"]["blacklistedwords"].insert_one({"_id": ctx.guild.id, "words": [words.lower()]})
            else:
                if words.lower() in document["words"]:
                    return
                else:
                    embed = discord.Embed(
                        title = "Blacklisted Words Updated",
                        description = f"`{words}` has been added to the blacklisted words list.",
                        color = Config.MAINCOLOR
                    )
                    Config.CLUSTER["servers"]["blacklistedwords"].update_one({"_id": ctx.guild.id}, {"$push": {"words": words.lower()}})
        await ctx.send(embed = embed)

    @blacklistedwords.command()
    async def remove(self, ctx, *, words = None):
        try:
            await ctx.message.delete()
        except discord.Forbidden:
            pass
        if words == None:
            return
        else:
            document = Config.CLUSTER["servers"]["blacklistedwords"].find_one({"_id": ctx.guild.id})
            if document == None:
                return
            else:
                if words.lower() not in document["words"]:
                    return
                else:
                    embed = discord.Embed(
                        title = "Blacklisted Words Updated",
                        description = f"`{words}` has been removed from the blacklisted words list.",
                        color = Config.MAINCOLOR
                    )
                    Config.CLUSTER["servers"]["blacklistedwords"].update_one({"_id": ctx.guild.id}, {"$pull": {"words": words.lower()}})
        await ctx.send(embed = embed)

def setup(bot):
    bot.add_cog(BlacklistingWords(bot))
