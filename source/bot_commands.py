import discord
import requests
import json
import os

from dotenv import load_dotenv
from source.utils import putTableAll, putTableLong, putFixtures, fetchJSON, putMatches
from source.league_code import LEAGUE_CODE
from source.team_id import TEAM_ID
from source.exceptions import *


def getStandings(code, mode='long'):
"""
    Funktion, die den Tabellenstand im Textformat liefert.
    Fragt den Cache nach den angeforderten Daten ab, falls nicht gefunden,
    Lädt die Daten von der API und speichert sie im Cache

    Parameter:
    -----------
    code: str
        Die ID der Liga, für die der Tabellenstand benötigt wird
    Modus: 'lang' oder 'alle', optional
        * Standardwert ist 'long'
        * 'long' -> SNO, Mannschaftsname, gespielte Spiele, erzielte Punkte
        * 'all' -> SNO, Mannschaftscode, Spiele, Gewonnen, Unentschieden, Verloren, Punkte, Tordifferenz

    Rückgabe:
    --------
    str
        Tabellenstand, wenn der Code gültig ist, oder eine Fehlermeldung

    """

    try:
        if code not in LEAGUE_CODE:
            raise InvalidLeagueCodeException

        obj = fetchJSON(code, 'standings')
        if mode == 'all':
            return putTableAll(obj)
        return putTableLong(obj)

    except InvalidLeagueCodeException:
        return None


def getFixtures(code, limit: int):
    """
   Zeigt die Spiele der gewünschten Liga / Mannschaft als Embed an
    Holt die Spiele aus der JSON-Datei und zeigt sie als Einbettung an,
    Zeigt 'Limit' Spiele an

    Parameter:
    -----------
    code: str
        Die ID der Liga oder Mannschaft, für die Spielpläne benötigt werden
    Grenze: int, optional
        Anzahl der anzuzeigenden Spiele (Standardwert: 5)

    Rückgabe:
    --------
    discord.Embed
        Zeigt so viele Fixtures an, wie angefordert wurden,
        Im Falle eines ungültigen Codes wird die entsprechende Hilfe-Einbettung zurückgegeben

    """
    try:
        if limit < 0:
            raise InvalidLimitException

        mode = 'league'
        if code not in LEAGUE_CODE:
            if code in TEAM_ID:
                mode = 'team'
            else:
                return discord.Embed(title='Bitte geb einen richtigen League Code an zB. BL1',
                                     description='Bitte beachten Sie **.team-codes** für Team-Codes\
                        \nUnd **.League-Codes** für Liga-Codes',
                                     color=0xf58300)

        obj = fetchJSON(code, 'fixtures')
        return putFixtures(obj, code, limit, mode)

    except InvalidLimitException:
        return discord.Embed(title='Limit muss größer als null sein',
                             description="Geben Sie ein gültiges Limit ein",
                             color=0xf58300)


def getMatches(code, limit: int):
    try:
        if limit < 0:
            raise InvalidLimitException

        mode = 'league'
        if code not in LEAGUE_CODE:
            if code in TEAM_ID:
                mode = 'team'
            else:
                return discord.Embed(title='Bitte geben Sie einen gültigen Code ein!',
                                     description='Bitte beachten Sie **.team-codes** für Team-Codes\
                        \nUnd **.League-Codes** für Liga-Codes',
                                     color=0xf58300)

        obj = fetchJSON(code, 'live')
        return putMatches(obj, code, limit, mode)

    except InvalidLimitException:
        return discord.Embed(title='Limit muss größer als null sein',
                             description="Geben Sie ein gültiges Limit ein",
                             color=0xf58300)


def getLeagueCodes(title="League Codes"):
    """
    Returns Leagues and their codes as an Embed

    Parameters:
    -----------
    title: str, optional
        Title of the embed (by default: "League Codes")

    Returns:
    --------
    discord.Embed 
        Embed displaying league codes

    """

    embed = discord.Embed(
        title=title,
        description="Referenz Codes für :five: Ligen hier:",
        color=0xf58300)
    embed.add_field(name=':one: Premier League',
                    value='PL' + "\n\u200b", inline=False)
    embed.add_field(name=':two: La Liga', value='SPA' +
                    "\n\u200b", inline=True)
    embed.add_field(name=':three: Serie A', value='SA' +
                    "\n\u200b", inline=False)
    embed.add_field(name=':four: Bundesliga',
                    value='BL1' + "\n\u200b", inline=True)
    embed.add_field(name=':five:Ligue 1', value='FL1', inline=False)
    return embed


def getTeamCodes(title="Team Codes"):
    """
    Returns Teams and their codes as an Embed

    Parameters:
    -----------
    title: str, optional
        Title of the embed (by default: "Team Codes")

    Returns:
    --------
    discord.Embed 
        Embed displaying team codes

    """

    embed = discord.Embed(
        title=title,
        description="Codes für Beispiel Teams hier:",
        color=0xf58300)
    embed.set_thumbnail(
        url="https://i.imgur.com/K54va2O.jpg")
    embed.add_field(name='SV Werder Bremen', value='SVW' + "\n\u200b", inline=True)
    embed.add_field(name='Bor. Mönchengladbach', value='BMG' + "\n\u200b", inline=True)
    embed.add_field(name='1. FC Union Berlin',
                    value='FCU' + "\n\u200b", inline=True)
    embed.add_field(name='Borussia Dortmund', value='BVB' + "\n\u200b", inline=True)
    embed.add_field(name='Bayern München', value='FCB' +
                    "\n\u200b", inline=True)
    embed.add_field(name='1. FSV Mainz 05', value='M05' + "\n\u200b", inline=True)
    embed.add_field(name='1. FC Köln', value='KOE' + "\n\u200b", inline=True)
    embed.add_field(name='SC Freiburg',
                    value='SCF' + "\n\u200b", inline=True)
    embed.add_field(name='Eintracht Frankfurt', value='SGE' + "\n\u200b", inline=True)
    embed.add_field(name='Bayer Leverkusen', value='B04', inline=True)
    return embed





def getHelpEmbed(ctx=None):
    """
    Generates the 'Help' embed when requested

    Parameters:
    -----------
    ctx: discord.Context
        Context data passed by discord when a command is invoked

    Returns:
    --------
    discord.Embed 
        Showing help data for the commands available

    """
    embed = discord.Embed(
        title="Fußball-HELP!",
        description="Zeigt verfügbare Befehle und deren Funktionen an\
                \nDas Befehlsprefix ist `.`",
        color=0xf58300)
    embed.set_thumbnail(
        url="https://i.imgur.com/vdIJoWJ.png")
    embed.add_field(name=":one: .standings-all [Liga Code]", inline=False,
                    value="> Detaillierte Rangliste, mit Team-Codes")
    embed.add_field(name=":two: .standings [Liga Code]", inline=False,
                    value="> Anzeigen der Rangliste")
    embed.add_field(name=":three: .fixtures [Liga Code oder Team Code]", inline=False,
                    value="> Zeigt Spielstände der Liga oder Mannschaft an",)
    embed.add_field(name=":four: .live [Liga Code oder Team Code]", inline=False,
                    value='> Live-Spiele der Liga oder Mannschaft anzeigen')
    embed.add_field(name=":five: .team-codes", inline=False,
                    value="> Zeigt Teams und ihre jeweiligen Codes an")
    
    if ctx is not None:
        embed.set_footer(text='Angefragt von: ' + str(ctx.author))

    return embed


if __name__ == "__main__":
    print(getStandings('PL'))
