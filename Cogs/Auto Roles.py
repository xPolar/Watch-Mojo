import discord
import pymongo
from discord.ext import commands

import Config

class AutoRoles(commands.Cog):

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
    
    @commands.Cog.listener()
    async def on_member_join(self, member):
        document = Config.CLUSTER["servers"]["autoroles"].find_one({"_id": member.guild.id})
        if document != None:
            roles = document["autoroles"]
            for role in roles:
                role_in_server = discord.utils.get(member.guild.roles, id = role)
                if role_in_server:
                    try:
                        await member.add_roles(role_in_server)
                    except discord.Forbidden:
                        print(f"[Auto Roles] I tried to add {role_in_server.name} - {role_in_server.id} to {member} - {member.id} but I don't have enough permissions to do so!")
                else:
                    roles.remove(role)
            if roles != document["autoroles"]:
                Config.CLUSTER["servers"]["autoroles"].update_one({"_id": member.guild.id}, {"$set": {"autorole": roles}})
    
    @commands.group()
    async def autorole(self, ctx):
        if ctx.invoked_subcommand == None:
            return

    @autorole.command()
    async def list(self, ctx):
        try:
            await ctx.message.delete()
        except discord.Forbidden:
            pass
        document = Config.CLUSTER["servers"]["autoroles"].find_one({"_id": ctx.guild.id})
        if document == None:
            return
        else:
            roles = document["autoroles"]
            roles_in_server = []
            for role in roles:
                role_in_server = discord.utils.get(ctx.guild.roles, id = role)
                if role_in_server:
                    roles_in_server.append(f"`{role_in_server.name}`")
                else:
                    roles.remove(role)
            if roles != document["autoroles"]:
                Config.CLUSTER["servers"]["autoroles"].update_one({"_id": ctx.guild.id}, {"$set": {"autoroles": roles}})
            if roles_in_server != []:
                roles_in_server[-1] = f"and {roles_in_server[-1]}" if len(roles_in_server) > 1 else roles_in_server[-1]
                embed = discord.Embed(
                    title = f"Auto-Role List",
                    description = ", ".join(roles_in_server) + ".",
                    color = Config.MAINCOLOR
                )
            else:
                return
        await ctx.send(embed = embed)
            
    @autorole.command()
    async def add(self, ctx, *, role : discord.Role = None):
        try:
            await ctx.message.delete()
        except discord.Forbidden:
            pass
        if role == None:
            return
        else:
            post = True
            document = Config.CLUSTER["servers"]["autoroles"].find_one({"_id": ctx.guild.id})
            if document != None:
                if role.id in document["autoroles"]:
                    post = False
            if post == False:
                return
            else:
                Config.CLUSTER["servers"]["autoroles"].update_one({"_id": ctx.guild.id}, {"$push": {"autoroles": role.id}}, upsert = True)
                embed = discord.Embed(
                    title = "Auto-Role Updated",
                    description = f"`{role.name}` has been added to the auto-role list.",
                    color = Config.MAINCOLOR
                )
        await ctx.send(embed = embed)

    @add.error
    async def add_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            return

    @autorole.command()
    async def remove(self, ctx, *, role : discord.Role = None):
        try:
            await ctx.message.delete()
        except discord.Forbidden:
            pass
        if role == None:
            return
        else:
            document = Config.CLUSTER["servers"]["autoroles"].find_one({"_id": ctx.guild.id})
            if document == None:
                return
            else:
                if role.id not in document["autoroles"]:
                    return
                else:
                    Config.CLUSTER["servers"]["autoroles"].update_one({"_id": ctx.guild.id}, {"$set": {"autoroles": document["autoroles"].remove(role.id)}})
                    document = Config.CLUSTER["servers"]["autoroles"].find_one({"_id": ctx.guild.id})
                    if document["autoroles"] == None:
                        Config.CLUSTER["servers"]["autoroles"].delete_one({"_id": ctx.guild.id})
                    embed = discord.Embed(
                        title = "Auto-Role Updated",
                        description = f"`{role.name}` has been removed from the auto-role list.",
                        color = Config.MAINCOLOR
                    )
        await ctx.send(embed = embed)
    
    @remove.error
    async def remove_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            return
    
def setup(bot):
    bot.add_cog(AutoRoles(bot))