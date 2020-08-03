import discord
import pymongo
from discord.ext import commands

import Config

class StickyRoles(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
    
    # REVIEW: Test the sticky roles feature and make sure commands work.
    
    @commands.Cog.listener()
    async def on_member_remove(self, member):
        roles = []
        for role in member.roles:
            roles.append(role.id)
        Config.CLUSTER["stickyroles"][f"{member.guild.id}"].insert_one({"_id": member.id, "roles": roles})
    
    @commands.Cog.listener()
    async def on_member_join(self, member):
        document = Config.CLUSTER["stickyroles"][f"{member.guild.id}"].find_one({"_id": member.id})
        if document != None:
            document_roles = document["roles"]
            roles = []
            for role in document_roles:
                roles.append(role)
            document = Config.CLUSTER["stickyroles"][f"{member.guild.id}"].find_one({"_id": "configuration"})
            if document != None:
                config = document["roles"]
                for role in config:
                    role_in_server = discord.utils.get(member.guild.roles, id = role)
                    if role_in_server == None:
                        config.remove(role)
                    if role in roles:
                        roles.remove(role)
                if config != document["roles"]:
                    Config.CLUSTER["stickyroles"][f"{member.guild.id}"].update_one({"_id": "configuration"}, {"$set": {"roles": config}})
            for role in roles:
                role_in_server = discord.utils.get(member.guild.roles, id = role)
                if role_in_server != None:
                    try:
                        await member.add_roles(role_in_server)
                    except discord.Forbidden:
                        print(f"[Sticky Roles] I tried to add {role_in_server.name} - {role_in_server.id} to {member} - {member.id} but I don't have enough permissions to do so!")
    
    @commands.group()
    @commands.has_permissions(manage_guild = True)
    async def stickyrole(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send_help("stickyrole")
    
    @stickyrole.command()
    async def list(self, ctx):
        document = Config["stickyroles"][f"{ctx.guild.id}"].find_one({"_id": "configuration"})
        if document == None:
            embed = discord.Embed(
                title = f"Sticky Roles for {ctx.guild.id} That Won't Be Given Back",
                description = f"Currently all roles under me will be given back to users when they rejoin a this server!",
                color = Config.MAINCOLOR
            )
        else:
            roles = document["roles"]
            roles_in_server = []
            for role in roles:
                role_in_server = discord.utils.get(ctx.guild.roles, id = role)
                if role_in_server != None:
                    roles_in_server.append(f"`{role_in_server.name}`")
                else:
                    roles.remove(role)
            if roles != document["roles"]:
                Config.CLUSTER["stickyroles"][f"{ctx.guild.id}"].update_one({"_id": "configuration"}, {"$set": {"roles": roles}})
            if roles_in_server != []:
                embed = discord.Embed(
                    title = f"Sticky Roles For {ctx.guild.id} That Won't Be Given Back",
                    description = ", ".join(roles_in_server),
                    color = Config.MAINCOLOR
                )
            else:
                embed = discord.Embed(
                    title = f"Sticky Roles for {ctx.guild.id}",
                    description = f"Currently all roles under me will be given back to users when they rejoin a this server!",
                    color = Config.MAINCOLOR
                )
        await ctx.send(embed = embed)

    @stickyrole.command()
    async def remove(self, ctx, role : discord.Role = None):
        if role == None:
            embed = discord.Embed(
                title = "Empty Argument",
                description = "Please provide a role you would like to remove from the sticky roles list!",
                color = Config.ERRORCOLOR
            )
        else:
            document = Config.CLUSTER["stickyroles"][f"{ctx.guild.id}"].find_one({"_id": "configuration"})
            if document == None:
                Config.CLUSTER["stickyroles"][f"{ctx.guild.id}"].insert_one({"_id": "configuration", "roles": [role.id]})
                embed = discord.Embed(
                    title = "Sticky Role Removed",
                    description = f"`{role.name}` has been removed from the list of sticky roles for this server!",
                    color = Config.MAINCOLOR
                )
            else:
                if role.id in document["roles"]:
                    embed = discord.Embed(
                        title = "Sticky Role Already Removed",
                        description = f"`{role.name}` has already been removed from the list of sticky roles for this server!",
                        color = Config.ERRORCOLOR
                    )
                else:
                    Config.CLUSTER["stickyroles"][f"{ctx.guild.id}"].insert_one({"_id": "configuration", "roles": [role.id]})
                    embed = discord.Embed(
                        title = "Sticky Role Removed",
                        description = f"`{role.name}` has been removed from the list of sticky roles for this server!",
                        color = Config.MAINCOLOR
                    )
        await ctx.send(embed = embed)

    @stickyrole.command()
    async def add(self, ctx, role : discord.Role = None):
        if role == None:
            embed = discord.Embed(
                title = "Empty Argument",
                description = "Please provide a role you would like to add to the sticky roles list!",
                color = Config.ERRORCOLOR
            )
        else:
            document = Config.ClUSTER["stickyroles"][f"{ctx.guild.id}"].find_one({"_id": "configuration"})
            if document == None:
                embed = discord.Embed(
                    title = "Sticky Role Already Added",
                    description = f"`{role.name}` has already been added to the list of sticky roles for this server!",
                    color = Config.MAINCOLOR
                )
            else:
                if role.id in document["roles"]:
                    embed = discord.Embed(
                        title = "Sticky Role Already Added",
                        description = f"`{role.name}` has already been added to the list of sticky roles for this server!",
                        color = Config.MAINCOLOR
                    )
                else:
                    document["roles"].remove(role.id)
                    Config.CLUSTER["stickyroles"][f"{ctx.guild.id}"].update_one({"_id": "configuration"}, {"$set": document})
                    embed = discord.Embed(
                        title = "Sticky Role Added",
                        description = f"`{role.name}` has been added to the list of sticky roles for this server!",
                        color = Config.MAINCOLOR
                    )
        await ctx.send(embed = embed)

def setup(bot):
    bot.add_cog(StickyRoles(bot))