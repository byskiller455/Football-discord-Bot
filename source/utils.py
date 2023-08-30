import json
import discord
import datetime as dt
import requests
import os


from dotenv import load_dotenv
from source.team_id import TEAM_ID
from source.league_code import LEAGUE_CODE


def putTableAll(obj):
    """
    Returns table as string showing standings of league with all data 

    Parameters:
    -----------
    obj: dict
        JSON object of league standings obtained from API/cache

    Returns:
    --------
    str
        Standings as a text code block (to get monospaced text) showing all data 
    """
    try:
        assert(type(obj) == dict)

        fin = open('source/teamcodes.json', 'r')
        mapper = json.load(fin)

        str_re = '```\nLIGA: ' + str(obj['competition']['name']) +\
                 ' ' * (45 - 2 - 8 - 10 - len(str(obj['competition']['name']))) +\
                 'SPIELTAG: ' + str(obj['season']['currentMatchday']) + '\n'
        str_re += '╔════╤══════╤════╤════╤════╤════╤═════╤═════╗\n'
        str_re += '║ SN │ TEAM │ M  │ W  │ D  │ L  │ PTS │ GD  ║\n'
        str_re += '╠════╪══════╪════╪════╪════╪════╪═════╪═════╣\n'
        for team in obj['standings'][0]['table']:
            text = '║ %-2d │ %-4s │ %-2d │ %-2d │ %-2d │ %-2d │ %-3d │ %+-3d ║\n'\
                % (team['position'], mapper.get(team['team']['name'], team['team']['name'][:4])[:4], team['playedGames'], team['won'],
                    team['draw'], team['lost'], team['points'], team['goalDifference'])

            str_re += text

        str_re += '╚════╧══════╧════╧════╧════╧════╧═════╧═════╝```'
        fin.close()
        return str_re

    except AssertionError:
        return 'Error!'


def putTableLong(obj):
    """
    Returns table as string with long team names and Matches played, Points alone

    Parameters:
    -----------
    obj: dict
        JSON object of league standings obtained from API/cache

    Returns:
    --------
    str
        Standings as code block (to get monospaced text) showing aforementioned data 
    """
    try:
        assert(type(obj) == dict)

        str_re = '```\nLIGA: ' + str(obj['competition']['name']) +\
                 ' ' * (45 - 2 - 8 - 10 - len(str(obj['competition']['name']))) +\
                 'SPIELTAG: ' + str(obj['season']['currentMatchday']) + '\n'
        str_re += '╔════╤══════════════════════════╤═════╤═════╗\n'
        str_re += '║ PL │        TEAM NAME         │ TD  │ PKT ║\n'
        str_re += '╠════╪══════════════════════════╪═════╪═════╣\n'
        for team in obj['standings'][0]['table']:
            text = '║ %-2d │ %-24s │ %-3d │ %-3d ║\n'\
                % (team['position'], team['team']['name'][:24], team['goalDifference'], team['points'])

            str_re += text

        str_re += '╚════╧══════════════════════════╧═════╧═════╝```'
        return str_re

    except AssertionError:
        return 'Error!'


def putFixtures(obj, code, limit, mode):
    """
    Returns Embed for fixtures of a league

    Parameters:
    -----------
    obj: dict
        JSON object of league standings obtained from API/cache
    code: str
        Code of the team/league for which fixtures are required
    limit: int
        Number of matches to display
    mode: str ['league' or 'team']
        Indicates which type of fixtures are to be generated

    Returns:
    --------
    discord.Embed
        Showing fixtures left in the league

    """
    if mode == 'league':
        title = obj['competition']['name']
    else:
        title = code
        with open('source/teamcodes.json') as fin:
            team_codes = json.load(fin)

        for key in team_codes.keys():
            if team_codes[key] == code:
                title = key

    fixtures = discord.Embed(title=title,
                             description='Spielzeiten',
                             color=0xf58300)
    if len(obj['matches']) == 0:
        fixtures.add_field(name='Keine verbleibenden Spiele in der aktuellen Saison!',
                           value='\u200b')
    else:
        for i, match in enumerate(obj['matches']):
            if i > limit - 1:
                break
            matchTime = dt.datetime.strptime(
                match['utcDate'][:-1], '%Y-%m-%dt%H:%M:%S')

            # Converting to IST from UTC
            matchTime += dt.timedelta(hours=2, minutes=0)
            homeTeam = match['homeTeam']['name']
            awayTeam = match['awayTeam']['name']

            date = matchTime.strftime('%d.%m.%Y')
            time = matchTime.strftime('%H:%M')
            fixtures.add_field(name=f'{homeTeam}  :regional_indicator_v::regional_indicator_s:  {awayTeam}',
                               value=f'`Datum:` {date}\n`Uhrzeit:` {time}' +
                               str('\n\u200b' if i != limit - 1 else ' '),
                               inline=False)
    return fixtures


def putMatches(obj, code, limit, mode):
    """
    Returns Embed for fixtures of a league

    Parameters:
    -----------
    obj: dict
        JSON object of league standings obtained from API/cache
    code: str
        Code of the team/league for which fixtures are required
    limit: int
        Number of matches to display
    mode: str ['league' or 'team']
        Indicates which type of fixtures are to be generated

    Returns:
    --------
    discord.Embed
        Showing fixtures left in the league

    """
    if mode == 'league':
        title = obj['competition']['name']
    else:
        title = code
        with open('source/teamcodes.json') as fin:
            team_codes = json.load(fin)

        for key in team_codes.keys():
            if team_codes[key] == code:
                title = key

    fixtures = discord.Embed(title=title,
                             description='Live Punkte Übersicht',
                             color=0xf58300)
    if len(obj['matches']) == 0:
        fixtures.add_field(name='Keine Live-Spiele im Moment!',
                           value='\u200b')
    else:
        fixtures.add_field(name='Heim Mannschaft   :regional_indicator_v::regional_indicator_s:   Auswärts Mannschaft',\
             value = '\u200b')
        for i, match in enumerate(obj['matches']):
            if i > limit - 1:
                break

            homeTeam = match['homeTeam']['name']
            awayTeam = match['awayTeam']['name']

            homeTeamScore = match['score']['fullTime']['homeTeam']
            homeTeamScore = 0 if homeTeamScore is None else homeTeamScore
            awayTeamScore = match['score']['fullTime']['awayTeam']
            awayTeamScore = 0 if awayTeamScore is None else awayTeamScore

            status = ''
            if homeTeamScore == awayTeamScore:
                status = f"**Spielstand: {homeTeamScore} - {awayTeamScore}**"
            else:
                leading = match['score']['winner']
                if leading == 'Auswärts_Mannschaft':
                    status = f"**Für {awayTeam} steht es gerade {awayTeamScore} - {homeTeamScore}**"
                else:
                    status = f"**Für {homeTeam} steht es gerade {homeTeamScore} - {awayTeamScore}**"

            fixtures.add_field(name=f'{homeTeam}  :regional_indicator_v::regional_indicator_s:  {awayTeam}',
                               value=status +
                               str('\n\u200b' if i != limit - 1 else ' '),
                               inline=False)
    return fixtures


def fetchJSON(code, resource):
    """
    Fetches and returns JSON object of the resource requested

    Parameters:
    -----------
    code: str
        The code representing the team or the league required
    resource: str ['fixtures' or 'standings or 'live']
        What resource of that league/team is requested

    Returns:
    --------
    dict
        JSON data fetched from cache or from API if cache miss
    """
    try:
        assert(resource in ['fixtures', 'standings', 'live'])

        if code in LEAGUE_CODE:
            id = LEAGUE_CODE.get(code)
            if resource == 'fixtures' or resource == 'live':
                resource += '-league'
        else:
            id = TEAM_ID.get(code)
            if resource == 'fixtures' or resource == 'live':
                resource += '-team'

        load_dotenv()
        url = "https://api.football-data.org/v4/"
        API_KEY = os.getenv('API_KEY')
        headers = {'X-Auth-Token': str(API_KEY)}

        extension = {'fixtures-league':
                     {'api': f"competitions/{id}/matches?status=SCHEDULED",
                      'file': f"cache/{code}-MAT.json"},
                     'standings':
                     {'api': f"competitions/{id}/standings",
                             'file': f"cache/{code}.json"},
                     'fixtures-team':
                     {'api': f"teams/{id}/matches?status=SCHEDULED",
                         'file': f"cache/TEAM-{code}.json"},
                     'live-league':
                     {'api': f"competitions/{id}/matches?status=LIVE",
                      'file': f"cache/{code}-LIVMAT.json"
                      },
                     'live-team':
                     {
                         'api': f"teams/{id}/matches?status=LIVE",
                         'file': f"cache/{code}-LIVMAT.json"
                     }
                     }

        # filePath = extension[resource]['file']

        # if os.path.exists(filePath):
        #     #Cache hit
        #     print(f'Entry for {code} found in Cache :D')

        #     with open(filePath, 'r') as fin:
        #         obj = json.load(fin)
        # else:
        # Cache Miss
        api_url = url + extension[resource]['api']
        r = requests.get(api_url, headers=headers)
        obj = r.json()

        # with open(extension[resource]['file'], 'w') as fout:
        #     json.dump(obj, fout, indent=4)

        return obj

    except AssertionError:
        return None


def fetchImage(code):
    """
    Returns file path to logo of league as string

    Parameters:
    -----------
    code : str
        The ID of the league for which fixtures are required

    Returns:
    --------
    str
        Contains file path if valid code is supplied, else 'None'
    """
    if code in ['PL', 'FL1', 'BL1', 'SPA', 'SA']:
        return f"source/logos/{code}.jpg"
    else:
        return None
