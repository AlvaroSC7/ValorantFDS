import json
import re
from valorantFDS_API import ValorantFDS_API
from PiumPiumBot_Config import PiumPiumBot_Config
from PiumPiumBot_ErrorCodes import ErrorCodes

api = ValorantFDS_API()
bot = PiumPiumBot_Config()
errorCode = ErrorCodes()

#To Do: implement snowflake
#To Do: encapsulate all functions within a class
#To Do: add logging with errors for PROD and performance + errors for DEV

##################################################################
#                         EXTERNAL FUNCTIONS                     #
##################################################################

def get_last_match_HS_percentage(region: str,name: str,tag: str,nMatches: int=1) -> float:
    """
        Get headshot percentage of a given player.

        Parameters:
            region      (str):  Player region
            name        (str):  Player user name
            tag         (str):  Player tag
            nMatches    (str):  Number of last matches to be analyzed
        Returns:
            Response: Headshot percentage of the given user
        """
    
    #Get last match data
    matches_request = api.get_lifetime_matches(region=region,name=name,tag=tag,size=1)
    #Parse data
    matchData = matches_request.json()
    _save_json(matchData,jsonName= "get_last_match_HS_percentage")

    #Check if player has changed its name
    if(matchData['status'] != 200):
        errorCode.handleErrorCode(errorCode= errorCode.ERR_CODE_100, httpError= matchData['status'])
        return errorCode.ERR_CODE_100
    
    if(len(matchData['data']) == 0):
       errorCode.handleErrorCode(errorCode= errorCode.ERR_CODE_101)
       return errorCode.ERR_CODE_101
    else:
        headshots = matchData['data'][0]['stats']['shots']['head']
        total_shots = headshots + matchData['data'][0]['stats']['shots']['body'] + matchData['data'][0]['stats']['shots']['leg']
        if(total_shots == 0):   #Player didn't shoot, avoid 0 div
            HS_accuracy = 0
        else:
            #Calculate accuracy
            HS_accuracy = round((headshots/total_shots) * 100,2)
        return HS_accuracy

def get_last_match_data(region: str,name: str,tag: str,target_player: str, target_team: str) -> str:
    """
        Proporciona el elo y porcentaje de tiro a la cabeza de cualquier jugador de tu ultima partida
        
        Ejemplos: !lg IMissHer !lg Sova enemy !lg Jett"
        """
    #Check first given command
    if(type(target_team) == str):    #Normalize only if it is not None
        target_team = target_team.lower()
    if(target_player == None):
        response = errorCode.handleErrorCode(errorCode.ERR_CODE_122)
    elif(target_team != None and target_team != "enemy" and target_team != "ally"):
        response = errorCode.handleErrorCode(errorCode.ERR_CODE_123)
    else:
        #Check if target is player name or player character
        normalized_target_player = _normalize_agent_map(target_player)
        target_type = _get_target_type(target= normalized_target_player)
        if(target_type == "map"):
            response = errorCode.handleErrorCode(errorCode.ERR_CODE_124)
        elif(target_type == "agent"):
            #Get elo and HS of the player controlling the selected agent in last player's game
            targetData = _get_last_match_agent_data(region= region, name= name, tag= tag, targetAgent= normalized_target_player, targetTeam= target_team)
            returnedErrorCode = errorCode.handleErrorCode(targetData)
            if(returnedErrorCode != None):
                response = returnedErrorCode
            else:
                response = _build_last_game_response(name= targetData['name'], elo= targetData['elo'], hs= targetData['HS'])
        else:   #It can be an error or just a player name
            #Get elo and HS of the selected player
            targetData = _get_last_match_player_data(region= region, name= name, tag= tag, targetName= target_player)
            returnedErrorCode = errorCode.handleErrorCode(targetData)
            if(returnedErrorCode != None):
                response = returnedErrorCode
            else:
                response = _build_last_game_response(name= target_player, elo= targetData['elo'], hs= targetData['HS'])
    return response

def get_player_data(player: str) -> dict:
    """
        Get Valorant user data depending on Discord user data.

        Parameters:
            player  (str):  Discord user name
        Returns:
            Response: Dictionary with the player region, name and tag.
        """
    try:
        with open(bot.PRIVATE_PATH + '/userList.json') as json_file:
            userList = json.load(json_file)
    except:
        return errorCode.handleErrorCode(errorCode.ERR_CODE_113)

    for user in userList['user']: 
        if(user['discord'] == str(player)):
            return user['gameData']
    
    errorCode.handleErrorCode(errorCode= errorCode.ERR_CODE_120)
    return errorCode.ERR_CODE_120    

def get_target_wr(region: str,name: str,tag: str, target: str) -> str:
    """
        Get WR percentage of a certain map or agent.

        Parameters:
            region      (str):  The Valorant region.
            name        (str):  The player name.
            tag         (str):  The player tag.
            target      (str):  String with the target (map or agent)
        Returns:
            Response    (float): WR of the player with the selected target .
        """
    targetStandard = _normalize_agent_map(target)
    targetType = _get_target_type(target= targetStandard)
    if(errorCode.isErrorCode(targetType) == True):
        return targetType
    else:
        #Get liffetime match data
        if(targetType == "map"):
            targetWR = _get_map_wr(region= region,name= name,tag= tag,map= targetStandard)
            if(errorCode.isErrorCode(targetWR) == True):
                return targetWR #Return error code
        elif(targetType == "agent"):
            targetWR = _get_agent_wr(region= region,name= name,tag= tag,agent= targetStandard)
            if(errorCode.isErrorCode(targetWR) == True):
                return targetWR #Return error code
        else:
            errorCode.handleErrorCode(errorCode= errorCode.ERR_CODE_121)
            return errorCode.ERR_CODE_121

        return targetWR

def get_mariano_lost_percentage() -> float:
    mariano = {'region': 'eu', 'name': 'Mariano', 'tag': "455"}
    #Get last match data
    matches_request = api.get_lifetime_matches(region= mariano['region'],name= mariano['name'],tag= mariano['tag'])
    #Parse data
    matchData = matches_request.json()
    _save_json(matchData,jsonName= "get_mariano_lost_percentage")
    #Get won and lost games
    mariano_won = 0
    mariano_lost = 0
    for game in matchData['data']:
        mariano_team = game['stats']['team'].lower()
        #Check that game is not DM
        if(mariano_team != "red" and mariano_team != "blue"):
            continue
        #Get each teams color
        if(mariano_team == "red"):
            opposite_team = "blue"
        else:
            opposite_team = "red"
        #Get each team score
        mariano_team_score = game['teams'][mariano_team]
        opposite_team_score = game['teams'][opposite_team]
        #Determine result based on score
        if(mariano_team_score > opposite_team_score):
            mariano_won = mariano_won + 1
        else:
            mariano_lost = mariano_lost + 1
    #Calculate loose percentage
    if(mariano_lost + mariano_won == 0):
       errorCode.handleErrorCode(errorCode= errorCode.ERR_CODE_102)
       return errorCode.ERR_CODE_102
    mariano_lost_percentage = (mariano_lost/(mariano_lost + mariano_won)) * 100
    return round(mariano_lost_percentage,2)

def get_this_season_elo(region: str,name: str,tag: str) -> str:
    """
        Get player elo in the active season

        Parameters:
            region  (str):  The Valorant region.
            name    (str):  The player name.
            tag     (str):  The player tag.
        Returns:
            Response: The player elo in the current season
        """
    elo = _get_elo(region= region, name= name, tag= tag)
    if(elo != None):
        result = elo[0] + " - " + str(elo[1])
    #Player is unranked, get level at least
    else:
        level = _get_level(region= region, name= name, tag= tag)
        if(errorCode.isErrorCode(level) == True):
            result = level #Return error code
        else:
            result = f"Unrated - Nivel {level}"
    
    return result

def get_avg_elo(region: str,name: str,tag: str) -> str:
    """
        Function that returns the average elo of each team of the user's last game.
        Parameters:
            region      (str):  The Valorant region.
            name        (str):  The player name.
            tag         (str):  The player tag.
        Returns:
            Response    (str): average elo of each team of the user's last game.
        """
    #Get last match data
    matches_request = api.get_v3_matches(region=region,name=name,tag=tag)
    #Parse data
    matchData = matches_request.json()
    _save_json(matchData,jsonName= "get_avg_elo")
    
    #Search for the selected player to get tag
    if(len(matchData['data']) == 0):
        errorCode.handleErrorCode(errorCode= errorCode.ERR_CODE_101)
        return errorCode.ERR_CODE_101   #Only error for this function is no matches found for the user

    lastGame = matchData['data'][0]
    player_and_opposite_team = _get_player_and_opposite_team(matchData= matchData, name= name, jsonVersion= "v3")
    avg_elo = {"red": 0, "blue": 0}
    for team in player_and_opposite_team:
        numOfPlayers = 0
        for player in lastGame['players'][team]:
            elo = _get_elo(region= region, name= player['name'], tag= player['tag'])
            if(errorCode.isErrorCode(elo) == True):
                return elo #Return error code
            elif(elo == None):  #Unrated player, skip for calculation
                continue
            else:
                eloNum = elo[1]
            avg_elo[team] = avg_elo[team] + eloNum
            numOfPlayers = numOfPlayers + 1
        if(numOfPlayers == 0):  #All unrated, return 0
            avg_elo[team] = 0
        else:
            avg_elo[team] = avg_elo[team] / numOfPlayers

    result = "Equipo aliado: \n\t" + _from_elo_to_rank(avg_elo[player_and_opposite_team[0]]) + "\nEquipo enemigo: \n\t" + _from_elo_to_rank(avg_elo[player_and_opposite_team[1]])
    return result

def peak_elo(region: str,name: str,tag: str, target_player: str, targetTeam: str= None) -> dict:
    """
        Function that implements the high level of get peak elo functions. It just checks input parameters and calls the right internal function
        Parameters:
            region          (str):  The Valorant region.
            name            (str):  The player name.
            tag             (str):  The player tag.
            target_player   (str):  The agent of the target player or his user name directly.
            targetTeam      (str):  The team of the target player (enemy or ally).
        Returns:
            Response        (str):  Bot response for the peak elo command
        """
    #Check first given command
    if(type(targetTeam) == str):    #Normalize only if it is not None
        targetTeam = targetTeam.lower()
    if(target_player == None):
        response = errorCode.handleErrorCode(errorCode.ERR_CODE_122)
    elif(targetTeam != None and targetTeam != "enemy" and targetTeam != "ally"):
        response = errorCode.handleErrorCode(errorCode.ERR_CODE_123)
    else:
        #Check if target is player name or player character
        normalized_target_player = _normalize_agent_map(target_player)
        target_type = _get_target_type(target= normalized_target_player)
        if(target_type == "map"):
            response = errorCode.handleErrorCode(errorCode.ERR_CODE_124)
        elif(target_type == "agent"):
            #Get elo and HS of the player controlling the selected agent in last player's game
            targetData = _get_last_match_agent_peak_elo(region= region, name= name, tag= tag, targetAgent= normalized_target_player, targetTeam= targetTeam)
            isErrorCode = errorCode.handleErrorCode(targetData)
            if(isErrorCode != None):
                response = isErrorCode
            else:
                peakDate = re.sub("e","Temporada ",targetData['peakEloDate'])
                peakDate = re.sub("(?<=[0-9])a(?=[0-9])"," Acto  ",peakDate)
                response = f"{targetData['name']}" + f"\n\t{targetData['peakElo']}" + f"\n\tFecha: {peakDate}"
        else:   #Can be an error or just a player name
            #Get elo and HS of the selected player
            targetData = _get_last_match_user_peak_elo(region= region, name= name, tag= tag, targetName= target_player)
            isErrorCode = errorCode.handleErrorCode(targetData)
            if(isErrorCode != None):
                response = isErrorCode
            else:
                peakDate = re.sub("e","Temporada ",targetData['peakEloDate'])
                peakDate = re.sub("(?<=[0-9])a(?=[0-9])"," Acto  ",peakDate)
                response = f"{targetData['name']}" + f"\n\t{targetData['peakElo']}" + f"\n\tFecha: {peakDate}"
    return response

def get_vct(competition: str, team: str= None) -> str:
    """
        Get next VCT upcoming matches information.

        Parameters:
            competition (str):  Name of the competition which information is going to be extracted
            team        (str):  If this parameter is provided, only this team information will be given as answer. If it is skipped, all league information is given
        Returns:
            Response: String with EMEA matches information
        """
    #Check if team and competition are valid
    availableCompetitions = ["vct_americas", "challengers_na", "game_changers_na", "vct_emea", "vct_pacific", "challengers_br", "challengers_jpn", "challengers_kr", "challengers_latam", "challengers_latam_n", "challengers_latam_s", "challengers_apac", "challengers_sea_id", "challengers_sea_ph", "challengers_sea_sg_and_my", "challengers_sea_th", "challengers_sea_hk_and_tw", "challengers_sea_vn", "valorant_oceania_tour", "challengers_south_asia", "game_changers_sea", "game_changers_series_brazil", "game_changers_east_asia", "game_changers_emea", "game_changers_jpn", "game_changers_kr", "game_changers_latam", "game_changers_championship", "masters", "last_chance_qualifier_apac", "last_chance_qualifier_east_asia", "last_chance_qualifier_emea", "last_chance_qualifier_na", "last_chance_qualifier_br_and_latam", "vct_lock_in", "champions", "vrl_spain", "vrl_northern_europe", "vrl_dach", "vrl_france", "vrl_east", "vrl_turkey", "vrl_cis", "mena_resilence", "challengers_italy", "challengers_portugal"]
    teams_emea = ["FUT","TH", "FNC", "NAVI", "KC", "VIT", "TL", "BBL", "M8", "KOI", "GX"]
    teams_na = ["LEV","KRU", "C9", "SEN", "G2", "100T", "EG", "NRG", "LOUD", "FURIA", "MIBR"]
    for comp in availableCompetitions:
        available_teams = {comp: []}
    available_teams['vct_emea'] = teams_emea
    available_teams['vct_americas'] = teams_na
    #Check if competition is known
    if(competition not in availableCompetitions):
        return errorCode.handleErrorCode(errorCode.ERR_CODE_111)
    #Check if team (if any) is known
    elif(team != None and team not in available_teams[competition]):
        return errorCode.handleErrorCode(errorCode.ERR_CODE_112)
    #Extract games data
    else:
        #Get last match data
        esport_request = api.get_esports_schedule(league= competition)
        #Parse data
        esportData = esport_request.json()
        _save_json(esportData,jsonName= "get_vct")

        #Check if player has changed its name
        if(esportData['status'] != 200):
            errorCode.handleErrorCode(errorCode= errorCode.ERR_CODE_100, httpError= esportData['status'])
            return errorCode.ERR_CODE_100

        if(len(esportData['data']) == 0):
           errorCode.handleErrorCode(errorCode= errorCode.ERR_CODE_101)
           return errorCode.ERR_CODE_101
        else:
            result = ""
            for game in esportData['data']:
                if(team == None or game['match']['teams'][0]['code'] == team or game['match']['teams'][1]['code'] == team): 
                    #All teams requested or exactly a match of the requested team
                    if(game['state'] == "completed"):
                        result = result + f"{game['match']['teams'][0]['name']} {game['match']['teams'][0]['game_wins']}-{game['match']['teams'][1]['game_wins']} {game['match']['teams'][1]['name']}" + "\n"
                    else:
                        result = result + game['match']['teams'][0]['name'] + " - " +  game['match']['teams'][1]['name'] + "  " + _translate_date(game['date']) + "\n"
            #Check if there is any data of the selected team or competition
            if(result == ""):
                result = errorCode.handleErrorCode(errorCode= errorCode.ERR_CODE_104)
            return result
        
def get_puuid(region: str,name: str,tag: str) -> str:
    """
        Get player puuid knowing its name, tag and region.

        Parameters:
            region      (str):  Player region
            name        (str):  Player user name
            tag         (str):  Player tag
        Returns:
            Response: User's puuid
        """
    
    #Get last match data
    matches_request = api.get_lifetime_matches(region=region,name=name,tag=tag,size=1)
    #Parse data
    matchData = matches_request.json()
    _save_json(matchData,jsonName= "get_puuid")

    #Check if player has changed its name
    if(matchData['status'] != 200):
        errorCode.handleErrorCode(errorCode= errorCode.ERR_CODE_100, httpError= matchData['status'])
        return errorCode.ERR_CODE_100
    
    if(len(matchData['data']) == 0):
       errorCode.handleErrorCode(errorCode= errorCode.ERR_CODE_101)
       return errorCode.ERR_CODE_101
    else:
        return matchData['data'][0]['stats']['puuid']

##################################################################
#                         INTERNAL FUNCTIONS                     #
##################################################################

def _save_json(data,jsonName: str):
    if(bot.type == "DEV"):
        with open (bot.TEMP_PATH + "/" + jsonName + ".json","w") as j:
            json.dump(data,j)

def _get_target_type(target: str) -> str:
    """
        Determine if target is an agent or a map.

        Parameters:
            target      (str):  String with the target (map or agent)
        Returns:
            Response    (str): Type of the target.
        """
    #Get content from API
    language = "es-ES"
    content = api.get_content(locale= language)
    contentData = content.json()
    _save_json(contentData,jsonName= "_get_target_type")
    
    maps = []
    agents = []
    #Extract all maps
    for map in contentData['maps']:
        if(map['name'] != "Null UI Data!"):
            maps.append(map['name'])
    #Extract all agents
    for agent in contentData['characters']:
        if(agent['name'] != "Null UI Data!"):
            agents.append(agent['name'])

    targetStandard = target.capitalize()  #Standarize target request
    if(targetStandard in maps):
        targetType = "map"
    elif(targetStandard in agents):
        targetType = "agent"
    else:
        targetType = None   #Could be an error or just a player name
    
    return targetType

#To Do: use this function in all the places it was hardcoded
def _get_player_and_opposite_team(matchData: json,name: str, jsonVersion: str) -> tuple:
        """
        Get the team a player was playing on in a certain json v3.

        Parameters:
            matchData   (json): Json file with all the data of the last game
            name        (str):  Name of the user
            jsonVersion (str):  Version of the used json file, v2 or v3
        Returns:
            Response: Tuple with first the team the player was on and second the other team
        """
        player_team = None
        #Extract the team of the player depending on json version
        if(jsonVersion.lower() == "v3"):
            if(len(matchData['data']) == 0):
                errorCode.handleErrorCode(errorCode= errorCode.ERR_CODE_101)
                return errorCode.ERR_CODE_101
            gameData = matchData['data'][0]['players']['all_players']
        elif(jsonVersion.lower() == "v2"):
            gameData = matchData['data']['players']['all_players']
        else:
            errorCode.handleErrorCode(errorCode= errorCode.ERR_CODE_110)
            return errorCode.ERR_CODE_110
        
        for player in gameData:
            if(player['name'] == name):
                player_team = player['team'].lower()
                break
        #Get opposite team
        if(player_team == "red"):
            opposite_team = "blue"
        elif(player_team == "blue"):
            opposite_team = "red"
        else:
            opposite_team = None
        return player_team, opposite_team

def _extract_player_data_with_agent_and_team(matchData: json,agent: str, team: str, jsonVersion: str) -> dict:
        """
        Looks for a player tag and name in a certain team knowing his agent.

        Parameters:
            matchData   (json): Json file with all the data of the last game
            agent       (str):  Name of the agent the target was using (or not)
            team        (str):  blue or red. Team to look in
            jsonVersion (str):  Version of the used json file, v2 or v3
        Returns:
            Response: Dictionary with the target tag and name with the tag of the target. None if no one played this agent in the selected team
        """
        if(jsonVersion.lower() == "v3"):
            if(len(matchData['data']) == 0):
                errorCode.handleErrorCode(errorCode= errorCode.ERR_CODE_101)
                return errorCode.ERR_CODE_101
            gameData = matchData['data'][0]['players'][team]
        elif(jsonVersion.lower() == "v2"):
            gameData = matchData['data']['players'][team]
        else:
            errorCode.handleErrorCode(errorCode= errorCode.ERR_CODE_110)
            return errorCode.ERR_CODE_110
        targetFound = False
        #Search for the selected player to get tag. First look in the enemy team
        for player in gameData:
            if(player['character'] == agent):
                targetName = player['name']
                targetTag = player['tag']
                targetFound = True
                break
        
        if(targetFound == False):
            return None
        else:
            return {'name': targetName, 'tag': targetTag}

def _get_agent_wr(region: str,name: str,tag: str, agent: str) -> float:
    """
        Get WR percentage of a certain map or agent.
        Parameters:
            region      (str):  The Valorant region.
            name        (str):  The player name.
            tag         (str):  The player tag.
            agent       (str):  String with the agent
        Returns:
            Response    (float): WR of the player with the selected agent .
        """
    matches_request = matches_request = api.get_lifetime_matches(region= region,name= name,tag= tag)
    matchesData = matches_request.json()
    _save_json(matchesData,jsonName= "_get_agent_wr")
    #Parse won and lost games
    wonMatches = 0
    lostMatches = 0
    for game in matchesData['data']:
        #Skip DM
        if(game['meta']['mode'] == "Deathmatch" or game['stats']['character']['name'] != agent.capitalize()):
            continue
        #If it's not a DM see who won
        team = game['stats']['team'].lower()
        if(team == "red"):
            opposite_team = "blue"
        else:
            opposite_team = "red"
        if(game['teams'][team] > game['teams'][opposite_team]):
            wonMatches = wonMatches + 1
        else:
            lostMatches = lostMatches + 1
    
    #Calculate win percentage in that map
    if(wonMatches + lostMatches == 0):
       errorCode.handleErrorCode(errorCode= errorCode.ERR_CODE_106)
       return errorCode.ERR_CODE_106
    agent_wr = (wonMatches/(wonMatches + lostMatches)) * 100
    return round(agent_wr,2)

def _get_map_wr(region: str,name: str,tag: str, map: str) -> float:
    """
        Get WR percentage of a certain map or agent.
        Parameters:
            region      (str):  The Valorant region.
            name        (str):  The player name.
            tag         (str):  The player tag.
            map         (str):  String with the map
        Returns:
            Response    (float): WR of the player with the selected target .
        """
    matches_request = api.get_lifetime_matches(region= region,name= name,tag= tag,map= map)
    matchesData = matches_request.json()
    _save_json(matchesData,jsonName= "_get_map_wr")

    #Parse won and lost games
    wonMatches = 0
    lostMatches = 0
    for game in matchesData['data']:
        #Skip DM
        if(game['meta']['mode'] == "Deathmatch"):
            continue
        #If it's not a DM see who won
        team = game['stats']['team'].lower()
        if(team == "red"):
            opposite_team = "blue"
        else:
            opposite_team = "red"
        if(game['teams'][team] > game['teams'][opposite_team]):
            wonMatches = wonMatches + 1
        else:
            lostMatches = lostMatches + 1
    
    #Calculate win percentage in that map
    if(wonMatches + lostMatches == 0):
       errorCode.handleErrorCode(errorCode= errorCode.ERR_CODE_105)
       return errorCode.ERR_CODE_105
    map_wr = (wonMatches/(wonMatches + lostMatches)) * 100
    return round(map_wr,2)

def _get_level(region: str,name: str,tag: str) -> int:
    """
        Get player level in the active season. Internal function

        Parameters:
            region  (str):  The Valorant region.
            name    (str):  The player name.
            tag     (str):  The player tag.
        Returns:
            Response: The player level (int)
        """
    level_request = api.get_lifetime_matches(region=region,name=name,tag=tag,size=1)
    levelData = level_request.json()
    _save_json(levelData,jsonName= "_get_level")
    if(len(levelData['data']) == 0):
        errorCode.handleErrorCode(errorCode= errorCode.ERR_CODE_101)
        return errorCode.ERR_CODE_101
    level = levelData['data'][0]['stats']['level']
    
    return level

def _get_elo(region: str,name: str,tag: str) -> tuple:
    """
        Get player elo in the active season. Internal function

        Parameters:
            region  (str):  The Valorant region.
            name    (str):  The player name.
            tag     (str):  The player tag.
        Returns:
            Response: The player elo in the current season as a tuple of rank(str) + elo (int)
        """
    #Get last match data
    elo_request = api.get_this_season_elo_api(region= region,name= name,tag= tag)
    #Parse data
    eloData = elo_request.json()
    _save_json(eloData,jsonName= "_get_elo")

    #Check if player has changed its name
    if(eloData['status'] != 200):   #To Do: add this check to every API call
        errorCode.handleErrorCode(errorCode= errorCode.ERR_CODE_100, httpError= eloData['status'])
        return errorCode.ERR_CODE_100

    #Player has a competitive rank
    if(eloData['data']['currenttierpatched'] != None and eloData['data']['elo'] != None):
        rank = eloData['data']['currenttierpatched']
        elo = eloData['data']['elo']
        result = rank, elo
    #Player is unranked, None
    else:
        result = None
    
    return result

def _from_elo_to_rank(elo: int) -> str:
    if(elo == 0):
        return "Unrated"
    ranks = ["Iron", "Bronze", "Silver", "Gold", "Platinum", "Diamond", "Ascendent", "Inmortal", "Radiant"]
    rankIndex = int(elo/300)
    rank = ranks[rankIndex]
    if(rank == "Radiant"):  #Radiant has no subranks
        result = rank
    else:
        subRank = int((elo - (300 * rankIndex)) / 100) + 1
        result = f"{rank} {subRank} - {int(elo)}"
    return result

def _get_last_match_ID(region: str,name: str,tag: str) -> str:
    """
        Get guiid for the last game of a certain player.

        Parameters:
            region      (str):  Player region
            name        (str):  Player user name
            tag         (str):  Player tag
        Returns:
            Response: Game ID of the last game of a certain player
        """
    
    #Get last match data
    matches_request = api.get_lifetime_matches(region=region,name=name,tag=tag,size=1)
    #Parse data
    matchData = matches_request.json()
    _save_json(matchData,jsonName= "_get_last_match_ID")
    if(len(matchData['data']) == 0):
       errorCode.handleErrorCode(errorCode= errorCode.ERR_CODE_101)
       return None
    else:
        game_id = matchData['data'][0]['meta']['id']
        return game_id
    
def _get_last_match_agent_peak_elo_old_game(name: str, gameId: str,targetAgent: str,targetTeam: str= None) -> dict:
    """
        Get target player elo and HS given the character he/she was playing in the last game. This version uses v2 API so it supports older games

        Parameters:
            gameId      (str):  Game ID
            targetAgent (str):  Agent that the target player was using
            targetTeam  (str):  Team where the targetAgent is being looked
        Returns:
            Response: Data for the player in the last user match
        """
    
    #Get last match data
    matches_request = api.get_lifetime_matches_by_matchId(matchId= gameId)
    #Parse data
    matchData = matches_request.json()
    _save_json(matchData,jsonName= "_get_last_match_agent_peak_elo_old_game")
    if(len(matchData['data']) == 0):
       errorCode.handleErrorCode(errorCode= errorCode.ERR_CODE_101)
       return errorCode.ERR_CODE_101

    #Get which team was the player on to start looking on the enemies side
    player_and_opposite_team = _get_player_and_opposite_team(matchData= matchData, name= name, jsonVersion= "v2")
    if(type(player_and_opposite_team) == str and errorCode.isErrorCode(player_and_opposite_team) == True):
        return player_and_opposite_team #Return error code
    else:
        player_team, opposite_team = player_and_opposite_team   #If it is not an error code it is a tupple
    
    if(type(targetTeam) == str):    #Normalize only if it is not None
        targetTeam = targetTeam.lower()
    
    targetData = None
    if(matchData['data'][0]['metadata']['mode_id'] == "deathmatch"):
        targetData = _extract_player_data_with_agent_and_team(matchData= matchData, agent= targetAgent, team= "all_players", jsonVersion= "v2")
        if(errorCode.isErrorCode(targetData) == True):
            return targetData #Return error code
    else:
    #Normal game, search by teams
        #Search for the selected player to get tag. First look in the enemy team
        if(targetTeam != "ally"):
            targetData = _extract_player_data_with_agent_and_team(matchData= matchData, agent= targetAgent, team= opposite_team, jsonVersion= "v2")
            if(errorCode.isErrorCode(targetData) == True):
                return targetData #Return error code

        #If no one was playing the agent in the enemy team, or ally team was explicitely selected, look in the player's team
        if((targetData == None and targetTeam == None) or (targetTeam == "ally")):
            targetData = _extract_player_data_with_agent_and_team(matchData= matchData, agent= targetAgent, team= player_team, jsonVersion= "v2")
            if(errorCode.isErrorCode(targetData) == True):
                return targetData #Return error code
    
    if(targetData == None):
        errorCode.handleErrorCode(errorCode= errorCode.ERR_CODE_103)
        return errorCode.ERR_CODE_103
    else:
        #Get data of the desired player
        region = matchData['data']['metadata']['region']
        peak_elo = _get_peak_elo(region= region,name= targetData['name'], tag= targetData['tag'])
        if(errorCode.isErrorCode(peak_elo) == True):
            return peak_elo #Return error code
        else:
            result = {'peakElo': peak_elo[0], 'peakEloDate': peak_elo[1], 'name': targetData['name']}
            return result

def get_player_tag_v3(matchData, name: str) -> str:
    """
        Get target tag knowing his name and a Json file of a v3 match including him.

        Parameters:
            matchData   (v3):   v3 json of a match played by the target
            name        (str):  Target user name
        Returns:
            Response:   (str):  Tag of the target
        """
    for player in matchData['data'][0]['players']['all_players']:
        if(str(player['name']) == name):
            return str(player['tag'])
    #If code is here no player with the selected name was found
    errorCode.handleErrorCode(errorCode= errorCode.ERR_CODE_102)
    return errorCode.ERR_CODE_102

def _get_peak_elo(region: str,name: str,tag: str) -> tuple:
    """
        Get highest rank a player has ever had

        Parameters:
            region      (str):  Player region
            name        (str):  Player user name
            tag         (str):  Player tag
        Returns:
            Response: String with the player's highest rank ever and season where he/she achieved it
        """
    
    #Get last match data
    puuid = get_puuid(region=region,name=name,tag=tag)
    elo_request = api.get_by_puuid_mmr_v2(region=region,puuid= puuid)
    #Parse data
    eloData = elo_request.json()
    _save_json(eloData,jsonName= "_get_peak_elo")

    #Check if player has changed its name
    if(eloData['status'] != 200):
        errorCode.handleErrorCode(errorCode= errorCode.ERR_CODE_100, httpError= eloData['status'])
        return errorCode.ERR_CODE_100
    else:
        highestRank = eloData['data']['highest_rank']['patched_tier']
        highestRankDate = eloData['data']['highest_rank']['season']
        return highestRank, highestRankDate
    
def _get_last_match_agent_peak_elo(region: str,name: str,tag: str,targetAgent: str,targetTeam: str= None) -> dict:
    """
        Get target player highest elo ever and when this was given the character he/she was playing in the last game.

        Parameters:
            region      (str):  Player region
            name        (str):  Player user name
            tag         (str):  Player tag
            targetAgent (str):  Agent that the target player was using
            targetTeam  (str):  Team where the targetAgent is being looked
        Returns:
            Response: Highest elo ever of the player in the last user match
        """
    
    #Get last match data
    matches_request = api.get_v3_matches(region=region,name=name,tag=tag)
    #Parse data
    matchData = matches_request.json()
    _save_json(matchData,jsonName= "_get_last_match_agent_peak_elo")
    if(len(matchData['data']) == 0):    #If there are no matches try another version of the API that allows older games
        gameId = _get_last_match_ID(region=region,name=name,tag=tag)
        if(gameId == None):
            errorCode.handleErrorCode(errorCode= errorCode.ERR_CODE_101)
            return errorCode.ERR_CODE_101   #Only error for this function is no matches found for the user
        else:
            return _get_last_match_agent_peak_elo_old_game(name= name, gameId= gameId, targetAgent= targetAgent, targetTeam= targetTeam)   #GameID v2 API support older games.

    #Get which team was the player on to start looking on the enemies side
    player_and_opposite_team = _get_player_and_opposite_team(matchData= matchData, name= name, jsonVersion= "v3")
    if(errorCode.isErrorCode(player_and_opposite_team) == True):
        return player_and_opposite_team #Return error code
    else:
        player_team, opposite_team = player_and_opposite_team   #If it is not an error code it is a tupple

    if(type(targetTeam) == str):    #Normalize only if it is not None
        targetTeam = targetTeam.lower()
    
    targetData = None
    if(matchData['data'][0]['metadata']['mode_id'] == "deathmatch"):
        targetData = _extract_player_data_with_agent_and_team(matchData= matchData, agent= targetAgent, team= "all_players", jsonVersion= "v3")
        if(errorCode.isErrorCode(targetData) == True):
            return targetData #Return error code
    else:
    #Normal game, search by teams
        #Search for the selected player to get tag. First look in the enemy team
        if(targetTeam != "ally"):
            targetData = _extract_player_data_with_agent_and_team(matchData= matchData, agent= targetAgent, team= opposite_team, jsonVersion= "v3")
            if(errorCode.isErrorCode(targetData) == True):
                return targetData #Return error code

        #If no one was playing the agent in the enemy team, or ally team was explicitely selected, look in the player's team
        if((targetData == None and targetTeam == None) or (targetTeam == "ally")):
            targetData = _extract_player_data_with_agent_and_team(matchData= matchData, agent= targetAgent, team= player_team, jsonVersion= "v3")
            if(errorCode.isErrorCode(targetData) == True):
                return targetData #Return error code
    
    if(targetData == None):
        errorCode.handleErrorCode(errorCode= errorCode.ERR_CODE_103)
        return errorCode.ERR_CODE_103
    else:
        #Get data of the desired player
        peak_elo = _get_peak_elo(region= region,name= targetData['name'], tag= targetData['tag'])
        if(errorCode.isErrorCode(peak_elo) == True):
            return peak_elo #Return error code
        else:
            result = {'peakElo': peak_elo[0], 'peakEloDate': peak_elo[1], 'name': targetData['name']}
            return result
        
def _get_last_match_user_peak_elo(region: str,name: str,tag: str, targetName: str) -> dict:
    """
        Get target player highest elo ever and when this was given his/her name.

        Parameters:
            region      (str):  Player region
            name        (str):  Player user name
            tag         (str):  Player tag
        Returns:
            Response: Highest elo ever of the player in the last user match
        """
    
    #Get last match data
    matches_request = api.get_v3_matches(region=region,name=name,tag=tag)
    #Parse data
    matchData = matches_request.json()
    _save_json(matchData,jsonName= "_get_last_match_user_peak_elo")
    if(len(matchData['data']) == 0):    #If there are no matches try another version of the API that allows older games
        errorCode.ERR_CODE_101   #Only error for this function is no matches found for the user
    
    #Get tag of the target user
    targetTag = get_player_tag_v3(matchData= matchData, name= targetName)
    if(errorCode.isErrorCode(targetTag) == True):
        return targetTag
    
    #Get data of the desired player
    peak_elo = _get_peak_elo(region= region,name= targetName, tag= targetTag)
    if(errorCode.isErrorCode(peak_elo) == True):
        return peak_elo #Return error code
    else:
        result = {'peakElo': peak_elo[0], 'peakEloDate': peak_elo[1], 'name': targetName}
        return result
    
def _get_last_match_agent_data(region: str,name: str,tag: str,targetAgent: str,targetTeam: str= None) -> dict:
    """
        Get target player elo and HS given the character he/she was playing in the last game.

        Parameters:
            region      (str):  Player region
            name        (str):  Player user name
            tag         (str):  Player tag
            targetAgent (str):  Agent that the target player was using
            targetTeam  (str):  Team where the targetAgent is being looked
        Returns:
            Response: Data for the player in the last user match
        """
    
    #Get last match data
    matches_request = api.get_v3_matches(region=region,name=name,tag=tag)
    #Parse data
    matchData = matches_request.json()
    _save_json(matchData,jsonName= "_get_last_match_agent_data")
    if(len(matchData['data']) == 0):
        gameId = _get_last_match_ID(region=region,name=name,tag=tag)
        if(gameId == None):
            return errorCode.ERR_CODE_101   #Only error for this function is no matches found for the user
        else:
            return _get_last_match_agent_data_old_game(name= name, gameId= gameId, targetAgent= targetAgent, targetTeam= targetTeam)   #GameID v2 API support older games.

    #Get which team was the player on to start looking on the enemies side
    player_and_opposite_team = _get_player_and_opposite_team(matchData= matchData, name= name, jsonVersion= "v3")
    if(errorCode.isErrorCode(player_and_opposite_team) == True):
        return player_and_opposite_team #Return error code
    else:
        player_team, opposite_team = player_and_opposite_team   #If it is not an error code it is a tupple

    if(type(targetTeam) == str):    #Normalize only if it is not None
        targetTeam = targetTeam.lower()
    
    targetData = None
    #If game is DM there are no teams
    if(matchData['data'][0]['metadata']['mode_id'] == "deathmatch"):
        targetData = _extract_player_data_with_agent_and_team(matchData= matchData, agent= targetAgent, team= "all_players", jsonVersion= "v3")
        if(errorCode.isErrorCode(targetData) == True):
            return targetData #Return error code
    else:
    #Normal game, search by teams
        #Search for the selected player to get tag. First look in the enemy team
        if(targetTeam != "ally"):
            targetData = _extract_player_data_with_agent_and_team(matchData= matchData, agent= targetAgent, team= opposite_team, jsonVersion= "v3")
            if(errorCode.isErrorCode(targetData) == True):
                return targetData #Return error code

        #If no one was playing the agent in the enemy team, or ally team was explicitely selected, look in the player's team
        if((targetData == None and targetTeam == None) or (targetTeam == "ally")):
            targetData = _extract_player_data_with_agent_and_team(matchData= matchData, agent= targetAgent, team= player_team, jsonVersion= "v3")
            if(errorCode.isErrorCode(targetData) == True):
                return targetData #Return error code
    
    if(targetData == None):
        errorCode.handleErrorCode(errorCode= errorCode.ERR_CODE_103)
        return errorCode.ERR_CODE_103
    else:
        #Get data of the desired player
        result = _extract_last_game_info(region= region, name= targetData['name'], tag = targetData['tag'], mode_id= matchData['data'][0]['metadata']['mode_id'])
        return result
        
def _get_last_match_player_data(region: str,name: str,tag: str,targetName: str) -> dict:
    """
        Get headshot percentage of a given player.

        Parameters:
            region      (str):  Player region
            name        (str):  Player user name
            tag         (str):  Player tag
            targetName  (str):  Name of the player (ally or enemy) whose data is being checked
        Returns:
            Response: Data for the player in the last user match
        """
    
    #Get last match data
    matches_request = api.get_v3_matches(region=region,name=name,tag=tag)
    #Parse data
    matchData = matches_request.json()
    _save_json(matchData,jsonName= "_get_last_match_player_data")
    
    #Search for the selected player to get tag
    if(len(matchData['data']) == 0):
        gameId = _get_last_match_ID(region=region,name=name,tag=tag)
        if(gameId == None):
            return errorCode.ERR_CODE_101   #Only error for this function is no matches found for the user
        else:
            return _get_last_match_player_data_old_game(gameId= gameId, targetName= targetName)   #GameID v2 API support older games.
    playerTag = get_player_tag_v3(matchData= matchData, name= targetName)
    if(errorCode.isErrorCode(playerTag) == True):
        return playerTag
    else:
        #Get data of the desired player
        result = _extract_last_game_info(region= region, name= targetName, tag = playerTag, mode_id= matchData['data'][0]['metadata']['mode_id'])
        return result
        
def _get_last_match_player_data_old_game(gameId: str, targetName: str) -> dict:
    """
        Get elo and headshot percentage of a given player knowing its game ID. Supports old games

        Parameters:
            gameId      (str):  Game ID
            targetName  (str):  Target user name
        Returns:
            Response: Data for the player in the last user match
        """
    
    #Get last match data
    matches_request = api.get_lifetime_matches_by_matchId(matchId= gameId)
    #Parse data
    matchData = matches_request.json()
    _save_json(matchData,jsonName= "_get_last_match_player_data_old_game")
    
    playerFound = False
    #Search for the selected player to get tag
    if(len(matchData['data']) == 0):
       errorCode.handleErrorCode(errorCode= errorCode.ERR_CODE_101)
       return errorCode.ERR_CODE_101
    for player in matchData['data']['players']['all_players']:
        if(str(player['name']) == targetName):
            playerName = str(player['name'])
            playerTag = str(player['tag'])
            playerFound = True
            break
    
    if(playerFound == False):
        errorCode.handleErrorCode(errorCode= errorCode.ERR_CODE_107)
        return errorCode.ERR_CODE_107
    else:
        #Get data of the desired player
        region = matchData['data']['metadata']['region']
        result = _extract_last_game_info(region= region, name= targetName, tag = playerTag, mode_id= matchData['data'][0]['metadata']['mode_id'])
        return result
        
def _get_last_match_agent_data_old_game(name: str, gameId: str,targetAgent: str,targetTeam: str= None) -> dict:
    """
        Get target player elo and HS given the character he/she was playing in the last game. This version uses v2 API so it supports older games

        Parameters:
            gameId      (str):  Game ID
            targetAgent (str):  Agent that the target player was using
            targetTeam  (str):  Team where the targetAgent is being looked
        Returns:
            Response: Data for the player in the last user match
        """
    
    #Get last match data
    matches_request = api.get_lifetime_matches_by_matchId(matchId= gameId)
    #Parse data
    matchData = matches_request.json()
    _save_json(matchData,jsonName= "_get_last_match_agent_data_old_game")
    if(len(matchData['data']) == 0):
       errorCode.handleErrorCode(errorCode= errorCode.ERR_CODE_101)
       return errorCode.ERR_CODE_101

    #Get which team was the player on to start looking on the enemies side
    player_and_opposite_team = _get_player_and_opposite_team(matchData= matchData, name= name, jsonVersion= "v2")
    if(type(player_and_opposite_team) == str and errorCode.isErrorCode(player_and_opposite_team) == True):
        return player_and_opposite_team #Return error code
    else:
        player_team, opposite_team = player_and_opposite_team   #If it is not an error code it is a tupple
    
    if(type(targetTeam) == str):    #Normalize only if it is not None
        targetTeam = targetTeam.lower()
    
    targetData = None
    if(matchData['data'][0]['metadata']['mode_id'] == "deathmatch"):
        targetData = _extract_player_data_with_agent_and_team(matchData= matchData, agent= targetAgent, team= "all_players", jsonVersion= "v2")
        if(errorCode.isErrorCode(targetData) == True):
            return targetData #Return error code
    else:
    #Normal game, search by teams
        #Search for the selected player to get tag. First look in the enemy team
        if(targetTeam != "ally"):
            targetData = _extract_player_data_with_agent_and_team(matchData= matchData, agent= targetAgent, team= opposite_team, jsonVersion= "v2")
            if(errorCode.isErrorCode(targetData) == True):
                return targetData #Return error code

        #If no one was playing the agent in the enemy team, or ally team was explicitely selected, look in the player's team
        if((targetData == None and targetTeam == None) or (targetTeam == "ally")):
            targetData = _extract_player_data_with_agent_and_team(matchData= matchData, agent= targetAgent, team= player_team, jsonVersion= "v2")
            if(errorCode.isErrorCode(targetData) == True):
                return targetData #Return error code
    
    if(targetData == None):
        errorCode.handleErrorCode(errorCode= errorCode.ERR_CODE_103)
        return errorCode.ERR_CODE_103
    else:
        #Get data of the desired player
        region = matchData['data']['metadata']['region']
        result = _extract_last_game_info(region= region, name= targetData['name'], tag = targetData['tag'], mode_id= matchData['data'][0]['metadata']['mode_id'])
        return result
        
def _translate_date(date: str) -> str:
    """
        Translate the date provided by the API calls to a more readable approach

        Parameters:
            date    (str):  Date as it is returned by the API calls
        Returns:
            Response: Date in a more readable format
        """
    
    #Get last match data
    year = re.findall("^[0-9]{4}", date)[0]
    month = re.findall("(?<=-)[0-9]{2}(?=-)", date)[0]
    day = re.findall("(?<=-)[0-9]{2}(?!-)", date)[0]
    hour = re.findall("(?<=[A-Z]{1})[0-9]{2}:[0-9]{2}", date)[0]
    return f"{day}/{month}/{year} {hour}"

def _normalize_agent_map(rawInput: str) -> str:
    """
        Normalize capital letter so all maps and agents are understood

        Parameters:
            rawInput    (str):  Agent or map as written by the user
        Returns:
            Response: Agent or map in correct format to be understood by API
        """   
    #Get last match data
    normalized = rawInput.capitalize()
    #Exception where normalize doesn't match the exact name used by Valorant API
    normalized = re.sub("Kay.*", "KAY/O", normalized)
    return normalized

def _extract_last_game_info(region: str, name: str, tag: str, mode_id: str) -> str:
        """
        Returns a dictionnary with all the data returned by !lg and similar commands. 
        Parameters:
            region      (str):  Player region
            name        (str):  Player user name
            tag         (str):  Player tag
            mode_id     (str):  ID of the mode of the last game  of the user
        Returns:
            Response: Data for the player in the last user match
        """
    #Get data of the desired player
        target_elo = get_this_season_elo(region= region,name= name, tag= tag)
        if(mode_id != "deathmatch"):
            target_HS = get_last_match_HS_percentage(region= region, name= name, tag= tag)
        else:
            target_HS = None    #RIOT does not track HS information for deathmatchs

        if(errorCode.isErrorCode(target_elo) == True):
            return target_elo #Return error code
        elif(errorCode.isErrorCode(target_HS) == True):
            return target_HS #Return error code
        else:
            result = {'elo': target_elo, 'HS': target_HS, 'name': name}
            return result
        
def _build_last_game_response(name: str, elo: str, hs: str):
    """
        Converts the dictionnary with all the last game data into the string returned by !lg and similar commands. 
        Parameters:
            region      (str):  Player region
            elo         (str):  Elo of the target player
            hs          (str):  Headshot percentage of the target player
        Returns:
            Response: String with the response of the bot for the !lg and similar commands
        """
    if(hs != None): # hs none means that RIOT does not track this for the last game mode
        response = f"{name}" + f"\n\t{elo}" + f"\n\tPorcentaje de headshot: {hs}%"
    else:
        response = f"{name}" + f"\n\t{elo}"
    return response

def main():
    name = "SpaguettiCoded"
    region = "eu"
    tag = "EUW"
    target = "Omen"
    print(get_puuid(region= "eu", name= "Jugador", tag= "peng1"))


if __name__ == "__main__":
    main()
