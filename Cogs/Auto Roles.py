import discord
import pymongo
from discord.ext import commands

import Config

class AutoRoles(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    # REVIEW: Test autorole commands and make sure roles are given when a user joins a server..
    
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
    @commands.has_permissions(manage_guild = True)
    async def autorole(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send_help("autorole")
    
    
    @autorole.command()
    async def list(self, ctx):
        document = Config.CLUSTER["servers"]["autoroles"].find_one({"_id": ctx.guild.id})
        if document == False:
            embed = discord.Embed(
                title = f"Auto Roles For {ctx.guild.name}",
                description = f"There are currently no auto roles for this server, to add one please do `{ctx.prefix}autorole add (Role)`!",
                color = Config.MAINCOLOR
            )
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
                embed = discord.Embed(
                    title = f"Auto Roles For {ctx.guild.name}",
                    description = ", ".join(roles_in_server),
                    color = Config.MAINCOLOR
                )
            else:
                embed = discord.Embed(
                    title = f"Auto Roles For {ctx.guild.name}",
                    description = f"There are currently no auto roles for this server, to add one please do `{ctx.prefix}autorole add (Role)`!",
                    color = Config.MAINCOLOR
                )
        await ctx.send(embed = embed)
            
    @autorole.command()
    async def add(self, ctx, *, role : discord.Role = None):
        if role == None:
            embed = discord.Embed(
                title = "Empty Argument",
                description = "Please provide a role to add to the auto role list!",
                color = Config.ERRORCOLOR
            )
        else:
            post = True
            document = Config.CLUSTER["servers"]["autoroles"].find_one({"_id": ctx.guild.id})
            if document != None:
                if role.id in document["autoroles"]:
                    post = False
            if post == False:
                embed = discord.Embed(
                    title = "Auto Role Already Added",
                    description = f"`{role.name}` is already in the list of auto roles for {ctx.guild.name}!",
                    color = Config.ERRORCOLOR
                )
            else:
                Config.CLUSTER["servers"]["autoroles"].update_one({"_id": ctx.guild.id}, {"$push": {"autoroles": role.id}}, upsert = True)
                embed = discord.Embed(
                    title = "Auto Role Added",
                    description = f"I have added `{role.name}` to the list of auto roles for {ctx.guild.name}!",
                    color = Config.MAINCOLOR
                )
        await ctx.send(embed = embed)

    @add.error
    async def add_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            embed = discord.Embed(
                title = "Invalid Argument",
                description = "Please provide a valid role!",
                color = Config.ERRORCOLOR
            )
            await ctx.send(embed = embed)

    @autorole.command()
    async def remove(self, ctx, *, role : discord.Role = None):
        if role == None:
            embed = discord.Embed(
                title = "Empty Argument",
                description = "Please provide a role to remove from the auto role list!",
                color = Config.ERRORCOLOR
            )
        else:
            document = Config.CLUSTER["servers"]["autoroles"].find_one({"_id": ctx.guild.id})
            if document == None:
                embed = discord.Embed(
                    title = "Auto Role Not Added",
                    descritpion = f"`{role.name}` isn't in the list of auto roles for {ctx.guild.name} so it can't be removed!",
                    color = Config.MAINCOLOR
                )
            else:
                if role.id not in document["autoroles"]:
                    embed = discord.Embed(
                        title = "Auto Role Not Added",
                        descritpion = f"`{role.name}` isn't in the list of auto roles for {ctx.guild.name} so it can't be removed!",
                        color = Config.MAINCOLOR
                    )
                else:
                    Config.CLUSTER["servers"]["autoroles"].update_one({"_id": ctx.guild.id}, {"$set": {"autoroles": document["autoroles"].remove(role.id)}})
                    embed = discord.Embed(
                        title = "Auto Role Removed",
                        description = f"`{role.name}` has been removed from the list of auto roles for {ctx.guild.name}!",
                        color = Config.MAINCOLOR
                    )
        await ctx.send(embed = embed)
    
    @remove.error
    async def remove_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            embed = discord.Embed(
                title = "Invalid Argument",
                description = "Please provide a valid role!",
                color = Config.ERRORCOLOR
            )
            await ctx.send(embed = embed)
    
def setup(bot):
    bot.add_cog(AutoRoles(bot))