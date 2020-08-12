import discord
import pymongo
from discord.ext import commands

import Config

class StickyRoles(commands.Cog):

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
                    if "roles" in document:
                        for role in ctx.author.roles:
                            if role.id in document["roles"]:
                                return True
    
    @commands.Cog.listener()
    async def on_member_remove(self, member):
        roles = [role.id for role in member.roles]
        Config.CLUSTER["stickyroles"][f"{member.guild.id}"].insert_one({"_id": member.id, "roles": roles})

    @commands.Cog.listener()
    async def on_member_join(self, member):
        document = Config.CLUSTER["stickyroles"][f"{member.guild.id}"].find_one({"_id": member.id})
        if document != None:
            sticky_roles_document = Config.CLUSTER["stickyroles"][f"{member.guild.id}"].find_one({"_id": "configuration"})
            if sticky_roles_document != None:
                for role in document["roles"]:
                    if role in sticky_roles_document["roles"]:
                        role_in_server = discord.utils.get(member.guild.roles, id = role)
                        if role_in_server != None:
                            if role_in_server.name != "@everyone":
                                try:
                                    await member.add_roles(role_in_server)
                                except discord.Forbidden:
                                    if member.guild_permissions.manage_roles:
                                        print(f"[Sticky Roles] I tried to add {role_in_server.name} ({role_in_server.id}) to {member} ({member.id}) in {member.guild} ({member.guild.id}) but I don't have enough permissions to do so, this is because the role is higher then me in the role hierarchy!")
                                    else:
                                        print(f"[Sticky Role] I don't have the MANAGE ROLES permission in {member.guild} ({member.guild.id}) which is required for stickyroles to function properly!")
                                        break
                                else:
                                    continue
            Config.CLUSTER["stickyroles"][f"{member.guild.id}"].delete_one({"_id": member.id})
    
    @commands.group()
    async def stickyrole(self, ctx):
        if ctx.invoked_subcommand == None:
            return
    
    @stickyrole.command()
    async def list(self, ctx):
        try:
            await ctx.message.delete()
        except discord.Forbidden:
            pass
        document = Config.CLUSTER["stickyroles"][f"{ctx.guild.id}"].find_one({"_id": "configuration"})
        if document == None:
            return
        else:
            roles = document["roles"]
            roles_in_server = []
            for role in roles:
                role_in_server = discord.utils.get(ctx.guild.roles, id = role)
                if role_in_server == None:
                    roles.remove(role)
                else:
                    roles_in_server.append(f"`{role_in_server}`")
            if roles != document["roles"]:
                Config.CLUSTER["stickyroles"][f"{ctx.guild.id}"].update_one({"_id": "configuration"}, {"$set": {"roles": roles}})
            if role_in_server != []:
                roles_in_server[-1] = f"and {roles_in_server[-1]}" if len(roles_in_server) > 1 else roles_in_server[-1]
                embed = discord.Embed(
                    title = "Sticky-Role List",
                    description = ", ".join(roles_in_server) + ".",
                    color = Config.MAINCOLOR
                )
            else:
                return
        await ctx.send(embed = embed)
    
    @stickyrole.command()
    async def add(self, ctx, role : discord.Role = None):
        try:
            await ctx.message.delete()
        except discord.Forbidden:
            pass
        if role == None:
            return
        else:
            document = Config.CLUSTER["stickyroles"][f"{ctx.guild.id}"].find_one({"_id": "configuration"})
            if document == None:
                embed = discord.Embed(
                    title = "Sticky-Role Updated",
                    description = f"`{role}` has been added to the sticky-role list.",
                    color = Config.MAINCOLOR
                )
                Config.CLUSTER["stickyroles"][f"{ctx.guild.id}"].insert_one({"_id": "configuration", "roles": [role.id]})
            else:
                if role.id in document["roles"]:
                    embed = discord.Embed(
                        title = "Error",
                        color = Config.ERRORCOLOR
                    )
                else:
                    embed = discord.Embed(
                        title = "Sticky-Role Updated",
                        description = f"`{role}` has been added to the sticky-role list.",
                        color = Config.MAINCOLOR
                    )
                    Config.CLUSTER["stickyroles"][f"{ctx.guild.id}"].update_one({"_id": "configuration"}, {"$push": {"roles": role.id}})
        await ctx.send(embed = embed)
    
    @add.error
    async def add_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            return

    @stickyrole.command()
    async def remove(self, ctx, role : discord.Role = None):
        try:
            await ctx.message.delete()
        except discord.Forbidden:
            pass
        if role == None:
            return
        else:
            document = Config.CLUSTER["stickyroles"][f"{ctx.guild.id}"].find_one({"_id": "configuration"})
            if document == None:
                return
            else:
                if role.id in document["roles"]:
                    embed = discord.Embed(
                        title = "Sticky-Role Updated",
                        description = f"`{role}` has been removed from the sticky-role list.",
                        color = Config.MAINCOLOR
                    )
                    Config.CLUSTER["stickyroles"][f"{ctx.guild.id}"].update_one({"_id": "configuration"}, {"$set": {"roles": document["roles"].remove(role.id)}})
                    if document["roles"] == []:
                        Config.CLUSTER["stickyroles"][f"{ctx.guild.id}"].delete_one({"_id": "configuration"})
                else:
                    return
        await ctx.send(embed = embed)

    @remove.error
    async def remove_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            return

def setup(bot):
    bot.add_cog(StickyRoles(bot))