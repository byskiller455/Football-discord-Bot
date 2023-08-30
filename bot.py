# bot.py
import os
import random

import source.bot_commands as bot_commands

import discord
from discord.ext import commands
from dotenv import load_dotenv
from source.utils import fetchImage

load_dotenv('.env')
TOKEN = os.getenv('DISCORD_TOKEN')

bot = commands.Bot(command_prefix='.')
bot.remove_command('help')


@bot.event
async def on_ready():
    print("Bot Funktioniert!")
    await bot.change_presence(
        activity=discord.Game(
            name=".help auf " + str(len(bot.guilds)) + " Servern")
    )


@bot.event
async def on_guild_join(guild):
    for channel in guild.text_channels:
        if channel.permissions_for(guild.me).send_messages:
            helpEmbed = bot_commands.getHelpEmbed()
            await channel.send('Hey, du! Wurde gerade diesem Kanal hinzugefügt!\
                \nGrundlegende Befehle sind unten aufgeführt :)', embed=helpEmbed)
            break



# Requires admin
@bot.command(name='update')
async def update(ctx, message = None):
    if ctx.message.author.id == 694128831291981844:
        for guild in bot.guilds:
            for channel in guild.text_channels:
                if channel.permissions_for(guild.me).send_messages:
                    helpEmbed = bot_commands.getHelpEmbed()
                    await channel.send(message, embed=helpEmbed)
                    break
            

@bot.command(name='standings-all', help='Zeigt die Rangliste mit allen Details an')
async def standingsAll(ctx, arg=''):
    text = bot_commands.getStandings(arg.upper(), mode='all')
    if text is not None:
        await ctx.send(text)
    else:
        leagueCodeEmbed = bot_commands.getLeagueCodes(
            'Ungültiger Liga-Code eingegeben!')
        await ctx.send(embed=leagueCodeEmbed)


@bot.command(name='standings', help='Anzeige der Rangliste mit nur gespielten Matches & Punkten')
async def standings(ctx, arg=''):
    text = bot_commands.getStandings(arg.upper(), mode='long')
    if text is not None:
        await ctx.send(text)
    else:
        leagueCodeEmbed = bot_commands.getLeagueCodes(
            'Ungültiger Liga-Code eingegeben!')
        await ctx.send(embed=leagueCodeEmbed)


@bot.command(name='fixtures', alias=['matches', 'm', 'f'])
async def fixtures(ctx, code = '', limit=5):
    fixturesEmbed = bot_commands.getFixtures(code.upper(), limit)
    fixturesEmbed.set_footer(text='Erfragt von: ' + str(ctx.author))

    path = fetchImage(code.upper())
    if path is not None:
        fixturesEmbed.set_thumbnail(url='attachment://image.jpg')
        await ctx.send(embed=fixturesEmbed, file=discord.File(path, 'image.jpg'))
    else:
        await ctx.send(embed=fixturesEmbed)

@bot.command(name='live', aliases=['l'])
async def matches(ctx, code='', limit=5):
    liveMatchesEmbed = bot_commands.getMatches(code.upper(), limit)
    liveMatchesEmbed.set_footer(text='Erfragt von: ' + str(ctx.author))
  
    path = fetchImage(code.upper())
    if path is not None:
        liveMatchesEmbed.set_thumbnail(url='attachment://image.jpg')
        await ctx.send(embed=liveMatchesEmbed, file=discord.File(path, 'image.jpg'))
    else:
        await ctx.send(embed=liveMatchesEmbed)

@bot.command(name='league-codes')
async def leagueCodes(ctx):
    leagueCodesEmbed = bot_commands.getLeagueCodes()
    leagueCodesEmbed.set_footer(text='Erfragt von: ' + str(ctx.author))
    await ctx.send(embed=leagueCodesEmbed)

@bot.command(name='team-codes')
async def teamCodes(ctx):
    teamCodesEmbed = bot_commands.getTeamCodes()
    teamCodesEmbed.set_footer(text='Erfragt von: ' + str(ctx.author))
    await ctx.send(embed=teamCodesEmbed)


@bot.command(name='help')
async def help(ctx):
    helpEmbed = bot_commands.getHelpEmbed(ctx)
    await ctx.send(embed=helpEmbed)

bot.run(TOKEN)