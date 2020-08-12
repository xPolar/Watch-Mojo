import discord
import pymongo
from discord.ext import commands

import Config

class BlacklistedNames(commands.Cog):

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
            if ctx.id in Config.OWNER_IDS or ctx.guild_permissions.manage_guild == True:
                return True
            else:
                document = Config.CLUSTER["servers"]["permissions"].find_one({"_id": ctx.guild.id})
                if document == None:
                    return False
                else:
                    for role in ctx.roles:
                        if role.id in document["roles"]:
                            return True
    
    def user_bypass_filter(self, ctx):
        return True if ctx.id in Config.OWNER_IDS else False

    @commands.Cog.listener()
    async def on_member_join(self, member):
        if member.bot == False and self.bypass_filter(ctx) == False:
            document = Config.CLUSTER["servers"]["badnames"].find_one({"_id": member.guild.id})
            if document != None:
                for name in document["names"]:
                    if name in member.name.lower():
                        await member.edit(nick = "[Content Moderated]")
                        return
        
    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        if after.bot == False and self.bypass_filter(after) == False:
            document = Config.CLUSTER["servers"]["badnames"].find_one({"_id": after.guild.id})
            if document != None:
                for name in document["names"]:
                    if name in after.display_name.lower():
                        await after.edit(nick = "[Content Moderated]")
                        return
    
    @commands.Cog.listener()
    async def on_user_update(self, before, after):
        if after.bot == False and self.user_bypass_filter(after) == False:
            for guild in self.bot.guilds:
                member = discord.utils.get(guild.members, id = after.id)
                if member != None:
                    document = Config.CLUSTER["servers"]["badnames"].find_one({"_id": member.guild.id})
                    if document != None:
                        for name in document["names"]:
                            if name in member.name.lower():
                                await member.edit(nick = "[Content Moderated]")
                                return
        
    @commands.group()
    async def blacklistednames(self, ctx):
        if ctx.invoked_subcommand == None:
            return
    
    @blacklistednames.command()
    async def list(self, ctx):
        try:
            await ctx.message.delete()
        except discord.Forbidden:
            pass
        document = Config.CLUSTER["servers"]["badnames"].find_one({"_id": ctx.guild.id})
        if document == None:
            return
        else:
            if document["names"] == []:
                return
            else:
                names = []
                for name in document["names"]:
                    names.append(f"`{name}`")
                names[-1] = f"and {names[-1]}" if len(name) > 1 else names[-1]
                embed = discord.Embed(
                    title = f"Blacklisted Names List",
                    description = ", ".join(names) + ".",
                    color = Config.MAINCOLOR
                )
        await ctx.send(embed = embed)
    
    @blacklistednames.command()
    async def add(self, ctx, *, name = None):
        try:
            await ctx.message.delete()
        except discord.Forbidden:
            pass
        if name == None:
            return
        else:
            document = Config.CLUSTER["servers"]["badnames"].find_one({"_id": ctx.guild.id})
            if document == None:
                embed = discord.Embed(
                    title = "Bad Blacklisted Names Updated",
                    description = f"I have added `{name}` to the list of bad names!",
                    color = Config.MAINCOLOR
                )
                Config.CLUSTER["servers"]["badnames"].insert_one({"_id": ctx.guild.id, "names": [name.lower()]})
            else:
                if name.lower() in document["names"]:
                        return
                else:
                    embed = discord.Embed(
                        title = "Blacklisted Names Updated",
                        description = f"`{name}` has been added to the blacklisted names list.",
                        color = Config.MAINCOLOR
                    )
                    Config.CLUSTER["servers"]["badnames"].update_one({"_id": ctx.guild.id}, {"$push": {"names": name.lower()}})
        await ctx.send(embed = embed)

    @blacklistednames.command()
    async def remove(self, ctx, *, name = None):
        try:
            await ctx.message.delete()
        except discord.Forbidden:
            pass
        if name == None:
           return
        else:
            document = Config.CLUSTER["servers"]["badnames"].find_one({"_id": ctx.guild.id})
            if document == None:
                    return
            else:
                if name.lower() not in document["names"]:
                        return
                else:
                    embed = discord.Embed(
                        title = "Blacklisted Names Updated",
                        description = f"`{name}` has been removed from the blacklisted names list.",
                        color = Config.MAINCOLOR
                    )
                    Config.CLUSTER["servers"]["badnames"].update_one({"_id": ctx.guild.id}, {"$pull": {"names": name.lower()}})
        await ctx.send(embed = embed)

def setup(bot):
    bot.add_cog(BlacklistedNames(bot))
