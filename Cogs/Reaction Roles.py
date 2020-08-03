import discord
import pymongo
from discord.ext import commands

import Config

class ReactionRoles(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
    
    @commands.command()
    @commands.has_permissions(manage_guild = True)
    async def reactionrole(self, ctx, message = None, emoji = None, role : discord.Role = None):
        if message == None:
            embed = discord.Embed(
                title = "Empty Argument",
                description = ""
            )

def setup(bot):
    bot.add_cog(ReactionRoles(bot))