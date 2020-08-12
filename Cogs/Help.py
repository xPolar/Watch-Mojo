import discord
import pymongo
from discord.ext import commands

import Config

class Help(commands.Cog):

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

    @commands.command()
    async def panel(self, ctx):
        try:
            await ctx.message.delete()
        except discord.Forbidden:
            pass
        embed = discord.Embed(
            title = "Bot Panel",
            description = "• System:\n  • Reboot: ?reboot.\n\n• Permission:\n  •?permission list.\n  •?permission add [...].\n  •?permission remove [...].\n\n• Auto-Role:\n  •?autorole list.\n  •?autorole add [...].\n  •?autorole remove [...].\n\n• Sticky-Role:\n  •?stickyrole list.\n  •?stickyrole add [...].\n  •?stickyrole remove [...].\n\n• Blacklist Words:\n  •?blacklistedwords list.\n  •?blacklistedwords add [...].\n  •?blacklistedwords remove [...].\n\n• Blacklist Names:\n  •?blacklistednames list.\n  •?blacklistednames add [...].\n  •?blacklistednames remove [...].",
            color = Config.MAINCOLOR
        )
        await ctx.send(embed = embed)

def setup(bot):
    bot.add_cog(Help(bot))