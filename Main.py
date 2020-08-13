import asyncio
import datetime

import discord
import pymongo
from discord.ext import commands

import Config

async def get_prefix(bot, message):
    if message.guild == None:
        return commands.when_mentioned_or(Config.PREFIX)(bot, message)
    else:
        prefixes = Config.CLUSTER["servers"]["prefixes"].find_one({"_id": message.guild.id})
        if prefixes == None:
            return commands.when_mentioned_or(Config.PREFIX)(bot, message)
        else:
            return commands.when_mentioned_or(prefixes["prefix"])(bot, message)

bot = commands.AutoShardedBot(command_prefix = get_prefix, case_insensitive = True)

bot.remove_command("help")

Cogs = ["Auto Roles", "Sticky Roles", "Blacklisting Words", "Bad Names", "Duplicated Messages", "Community Announcements", "Help", "Permission System", "Embeds"]

for Cog in Cogs:
    bot.load_extension(f"Cogs.{Cog}")
    print(f"Cog Started | {Cog} has started!")

def perm_check(ctx):
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
                    for roles in ctx.guild.roles:
                        if role.id in document["roles"]:
                            return True

@bot.command()
@commands.check(perm_check)
async def reboot(ctx, cog = None):
    """
    Restart the bot's Cogs.
    """
    if cog != None:
        cog = cog.lower()
        bot.reload_extension(f"Cogs.{cog}")
        print(f"Cog Restarted | {cog} has been restarted!")
        embed = discord.Embed(
            title = f"Rebooted {cog}",
            description = f"I have rebooted Cog: {cog}!",
            color = Config.MAINCOLOR
        )
        await ctx.send(embed = embed)
    else:
        str = ""
        for cog in Cogs:
            bot.reload_extension(f"Cogs.{cog}")
            print(f"Cog Restarted | {cog} has been restarted!")
        embed = discord.Embed(
            title = "Reboot",
            description = "`System`, `Permission`, `Auto-Role`, `Sticky-Role`, `Blacklist Words`, and `Blacklist Names` have been rebooted.",
            color = Config.MAINCOLOR
        )
        msg = await ctx.send(embed = embed)
        print(f"Cogs Restarted | I'm currently in {len(bot.guilds)} servers with {len(bot.users)} users!")
        try:
            await ctx.message.delete()
        except discord.Forbidden:
            return

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return
    elif isinstance(error, commands.BadArgument):
        return
    elif isinstance(error, commands.CheckFailure):
        embed = discord.Embed(
            title = "Error",
            color = Config.ERRORCOLOR
        )
        await ctx.send(embed = embed)
    else:
        raise error

@bot.event
async def on_shard_ready(shard_id):
    print(f"Shard Started | Shard {shard_id} has started!")

@bot.event
async def on_ready():
    print(f"Bot Started | I'm currently in {len(bot.guilds)} servers with {len(bot.users)} users!")

bot.run(Config.TOKEN)
