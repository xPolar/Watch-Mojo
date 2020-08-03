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

Cogs = ["Announcements", "Auto Roles", "Sticky Roles", "Video Announcements"]

for Cog in Cogs:
    bot.load_extension(f"Cogs.{Cog}")
    print(f"Cog Started | {Cog} has started!")

async def owner(ctx):
    return ctx.author.id in Config.OWNER_IDS

@bot.command()
@commands.check(owner)
async def restart(ctx, cog = None):
    """
    Restart the bot's Cogs.
    """
    if cog != None:
        cog = cog.lower()
        bot.reload_extension(f"Cogs.{cog}")
        print(f"Cog Restarted | {cog} has been restarted!")
        embed = discord.Embed(
                title = f"Restarted {cog}",
                description = f"I have restarted Cog: {cog}!",
                color = Config.MAINCOLOR
        )
        await ctx.send(embed = embed)
    else:
        embed = discord.Embed(
                title = "Restarting",
                color = Config.MAINCOLOR
        )
        msg = await ctx.send(embed = embed)
        for cog in Cogs:
            bot.reload_extension(f"Cogs.{cog}")
            print(f"Cog Restarted | {cog} has been restarted!")
            embed.add_field(name = cog, value = "🔄 Restarted")
            await msg.edit(embed = embed)
        print(f"Cogs Restarted | I'm currently in {len(bot.guilds)} servers with {len(bot.users)} users!")
        await asyncio.sleep(3)
        await msg.delete()
        if ctx.guild != None:
            try:
                await ctx.message.delete()
            except:
                pass

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return
    elif isinstance(error, commands.BadArgument):
        return
    elif isinstance(error, commands.CheckFailure):
        embed = discord.Embed(
            title = "Missing Permissions",
            description = "You don't have enough permissions to run this command",
            color = Config.ERRORCOLOR
        )
        await ctx.send(embed = embed)
    else:
        try:
            embed = discord.Embed(
                    title = "Error",
                    description = f"**```\n{error}\n```**",
                    color = Config.ERRORCOLOR
            )
            embed.set_footer(text = f"Please report this to my developer by joining our support server with the link located on {ctx.prefix}help")
            await ctx.send(embed = embed)
        except:
            return
        raise error

@bot.event
async def on_shard_ready(shard_id):
    print(f"Shard Started | Shard {shard_id} has started!")

@bot.event
async def on_ready():
    print(f"Bot Started | I'm currently in {len(bot.guilds)} servers with {len(bot.users)} users!")
    await bot.change_presence(status = discord.Status.dnd, activity = discord.Game("with ?help"))

bot.run(Config.TOKEN)
