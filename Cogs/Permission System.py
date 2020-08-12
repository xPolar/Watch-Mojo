import discord
import pymongo
from discord.ext import commands

import Config

class PermissionSystem(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
    
    def cog_check(self, ctx):
        if ctx.guild == None:
            return False
        else:
            if ctx.author.id in Config.OWNER_IDS or ctx.author.guild_permissions.manage_guild == True:
                return True
            else:
                return False
    
    @commands.group()
    async def permission(self, ctx):
        if ctx.invoked_subcommand is None:
            return
    
    @permission.command()
    async def list(self, ctx):
        try:
            await ctx.message.delete()
        except discord.Forbidden:
            pass
        document = Config.CLUSTER["servers"]["permissions"].find_one({"_id": ctx.guild.id})
        if document == None:
            return
        else:
            roles_in_server = []
            if "roles" not in document:
                return
            else:
                for role in document["roles"]:
                    role_in_server = discord.utils.get(ctx.guild.roles, id = role)
                    if role_in_server != None:
                        roles_in_server.append(f"`{role_in_server}`")
                    else:
                        Config.CLUSTER["servers"]["permissions"].update_one({"_id": ctx.guild.id}, {"$pull": {"roles": role}})
                if roles_in_server != []:
                    roles_in_server[-1] = f"and {roles_in_server[-1]}" if len(roles_in_server) > 1 else roles_in_server[-1]
                    embed = discord.Embed(
                        title = "Permission List",
                        description = ", ".join(roles_in_server) + ".",
                        color = Config.MAINCOLOR
                    )
                else:
                    return
        await ctx.send(embed = embed)
    
    @permission.command()
    async def add(self, ctx, role : discord.Role = None):
        try:
            await ctx.message.delete()
        except discord.Forbidden:
            pass
        if role == None:
            return
        else:
            document = Config.CLUSTER["servers"]["permissions"].find_one({"_id": ctx.guild.id})
            if document == None:
                embed = discord.Embed(
                    title = "Permission Update",
                    description = f"`{role}` has been added to the permission list.",
                    color = Config.MAINCOLOR
                )
                Config.CLUSTER["servers"]["permissions"].insert_one({"_id": ctx.guild.id, "roles": [role.id]})
            else:
                if "roles" in document:
                    if role.id in document["roles"]:
                        embed = discord.Embed(
                            title = "Error",
                            color = Config.ERRORCOLOR
                        )
                    else:
                        embed = discord.Embed(
                            title = "Permission Update",
                            description = f"`{role}` has been added to the permission list.",
                            color = Config.MAINCOLOR
                        )
                        Config.CLUSTER["servers"]["permissions"].update_one({"_id": ctx.guild.id}, {"$push": {"roles": role.id}})
                else:
                    embed = discord.Embed(
                        title = "Permission Update",
                        description = f"`{role}` has been added to the permission list.",
                        color = Config.MAINCOLOR
                    )
                    Config.CLUSTER["servers"]["permissions"].update_one({"_id": ctx.guild.id}, {"$push": {"roles": role.id}})
        await ctx.send(embed = embed)
    
    @add.error
    async def add_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            return
    
    @permission.command()
    async def remove(self, ctx, role : discord.Role = None):
        try:
            await ctx.message.delete()
        except discord.Forbidden:
            pass
        if role == None:
            return
        else:
            document = Config.CLUSTER["servers"]["permissions"].find_one({"_id": ctx.guild.id})
            if document == None:
                return
            else:
                if "roles" not in document:
                    return 
                else:
                    if role.id in document["roles"]:
                        embed = discord.Embed(
                            title = "Permission Update",
                            description = f"`{role}` has been removed from the permission list.",
                            color = Config.MAINCOLOR
                        )
                        Config.CLUSTER["servers"]["permissions"].update_one({"_id": ctx.guild.id}, {"$pull": {"roles": role.id}})
                        if document["roles"] == []:
                            Config.CLUSTER["servers"]["permissions"].delete_one({"_id": ctx.guild.id})
                    else:
                        return
            await ctx.send(embed = embed)

    @remove.error
    async def remove_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            return

def setup(bot):
    bot.add_cog(PermissionSystem(bot))