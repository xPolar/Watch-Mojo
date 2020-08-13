import discord
import pymongo
from discord.ext import commands

import Config

class Announcements(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    # REVIEW: Test announcement command.
    
    @commands.command()
    @commands.has_permissions(manage_guild = True)
    async def announce(self, ctx, channel = None, *, announcement = None):
        if channel == None:
            embed = discord.Embed(
                title = "Empty Argument",
                description = "Please provide something to announce!",
                color = Config.ERRORCOLOR
            )
            await ctx.send(embed = embed)
        else:
            text_channel = None
            if announcement == None:
                if channel.isdigit() == True:
                    text_channel = discord.utils.get(ctx.guild.text_channels, id = int(channel))
                if text_channel == None and channel[2:-1].isdigit() == True:
                    text_channel = discord.utils.get(ctx.guild.text_channels, id = int(channel[2:-1]))
                if text_channel == None:
                    text_channel = ctx.channel
                    announcement = channel
                else:
                    embed = discord.Embed(
                        title = "Empty Argument",
                        description = "Please provide something to announce!",
                        color = Config.ERRORCOLOR
                    )
                    await ctx.send(embed = embed)
                    return
            else:
                if channel.isdigit() == True:
                    text_channel = discord.utils.get(ctx.guild.text_channels, id = int(channel))
                if text_channel == None and channel[2:-1].isdigit() == True:
                    text_channel = discord.utils.get(ctx.guild.text_channels, id = int(channel[2:-1]))
                if text_channel == None:
                    text_channel = ctx.channel
                    announcement = channel + " " + announcement
                else:
                    embed = discord.Embed(
                        title = "Announcement Sent",
                        description = f"I have sent your announcement into {text_channel.mention}!",
                        color = Config.MAINCOLOR
                    )
                    await ctx.send(embed = embed)
            embed = discord.Embed(
                description = announcement,
                color = Config.MAINCOLOR
            )
            embed.set_author(name = f"Announcement by {ctx.author}!", icon_url = ctx.author.avatar_url)
            if announcement.lower().endswith("~e"):
                embed.description = embed.description[:-2]
                await text_channel.send("@everyone", embed = embed)
            elif announcement.lower().endswith("~h"):
                embed.description = embed.description[:-2]
                await text_channel.send("@here", embed = embed)
            else:
                await text_channel.send(embed = embed)

def setup(bot):
    bot.add_cog(Announcements(bot))