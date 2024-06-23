import json
from valorantFDS_API import ValorantFDS_API
from PiumPiumBot_Config import PiumPiumBot_Config
from PiumPiumBot_ErrorCodes import ErrorCodes

api = ValorantFDS_API()
bot = PiumPiumBot_Config()
errorCode = ErrorCodes()

#To Do: implement snowflake
#To Do: encapsulate all functions within a class

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
        print(f"{errorCode.ERR_CODE_100} - API returned error code {matchData['status']}")
        return errorCode.ERR_CODE_100
    
    if(len(matchData['data']) == 0):
       print(f"{errorCode.ERR_CODE_101} - No recent games found for the user")
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

def get_last_match_player_data(region: str,name: str,tag: str,targetName: str) -> dict:
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
    _save_json(matchData,jsonName= "get_last_match_player_data")
    
    playerFound = False
    #Search for the selected player to get tag
    if(len(matchData['data']) == 0):
        gameId = _get_last_match_ID(region=region,name=name,tag=tag)
        if(gameId == None):
            return errorCode.ERR_CODE_101   #Only error for this function is no matches found for the user
        else:
            return get_last_match_player_data_old_game(gameId= gameId, targetName= targetName)   #GameID v2 API support older games.
    for player in matchData['data'][0]['players']['all_players']:
        if(str(player['name']) == targetName):
            playerName = str(player['name'])
            playerTag = str(player['tag'])
            playerFound = True
            break
    
    if(playerFound == False):
        print(f"{errorCode.ERR_CODE_102} - Player not found in last game")
        return errorCode.ERR_CODE_102
    else:
        #Get data of the desired player
        player_elo = get_this_season_elo(region= region,name= playerName, tag= playerTag)
        player_HS = get_last_match_HS_percentage(region= region, name= playerName, tag= playerTag)
        if(errorCode.isErrorCode(player_elo) == True):
            return player_elo #Return error code
        elif(errorCode.isErrorCode(player_HS) == True):
            return player_HS #Return error code
        else:
            result = {'elo': player_elo, 'HS': player_HS}
            return result
    
def get_last_match_player_data_old_game(gameId: str, targetName: str) -> dict:
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
    _save_json(matchData,jsonName= "get_last_match_player_data_old_game")
    
    playerFound = False
    #Search for the selected player to get tag
    if(len(matchData['data']) == 0):
       print(f"{errorCode.ERR_CODE_101} - No games found even with v2 gameID API")
       return errorCode.ERR_CODE_101
    for player in matchData['data']['players']['all_players']:
        if(str(player['name']) == targetName):
            playerName = str(player['name'])
            playerTag = str(player['tag'])
            playerFound = True
            break
    
    if(playerFound == False):
        print(f"{errorCode.ERR_CODE_102} - Player not found in last game, even using v2 API")
        return errorCode.ERR_CODE_102
    else:
        #Get data of the desired player
        region = matchData['data']['metadata']['region']
        player_elo = get_this_season_elo(region= region,name= playerName, tag= playerTag)
        player_HS = get_last_match_HS_percentage(region= region, name= playerName, tag= playerTag)
        if(errorCode.isErrorCode(player_elo) == True):
            return player_elo #Return error code
        elif(errorCode.isErrorCode(player_HS) == True):
            return player_HS #Return error code
        else:
            result = {'elo': player_elo, 'HS': player_HS}
            return result
    
def get_last_match_agent_data(region: str,name: str,tag: str,targetAgent: str,targetTeam: str= None) -> dict:
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
    _save_json(matchData,jsonName= "get_last_match_agent_data")
    if(len(matchData['data']) == 0):
        gameId = _get_last_match_ID(region=region,name=name,tag=tag)
        if(gameId == None):
            return errorCode.ERR_CODE_101   #Only error for this function is no matches found for the user
        else:
            return get_last_match_agent_data_old_game(name= name, gameId= gameId, targetAgent= targetAgent, targetTeam= targetTeam)   #GameID v2 API support older games.

    #Get which team was the player on to start looking on the enemies side
    player_and_opposite_team = _get_player_and_opposite_team(matchData= matchData, name= name, jsonVersion= "v3")
    if(errorCode.isErrorCode(player_and_opposite_team) == True):
        return player_and_opposite_team #Return error code
    else:
        player_team, opposite_team = player_and_opposite_team   #If it is not an error code it is a tupple

    if(type(targetTeam) == str):    #Normalize only if it is not None
        targetTeam = targetTeam.lower()
    
    targetData = None
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
        print(f"{errorCode.ERR_CODE_103} - No player was using {targetAgent} in the last game of {name} #{tag}")
        return errorCode.ERR_CODE_103
    else:
        #Get data of the desired player
        target_elo = get_this_season_elo(region= region,name= targetData['name'], tag= targetData['tag'])
        target_HS = get_last_match_HS_percentage(region= region, name= targetData['name'], tag= targetData['tag'])
        if(errorCode.isErrorCode(target_elo) == True):
            return target_elo #Return error code
        elif(errorCode.isErrorCode(target_HS) == True):
            return target_HS #Return error code
        else:
            result = {'elo': target_elo, 'HS': target_HS, 'name': targetData['name']}
            return result
    
def get_last_match_agent_data_old_game(name: str, gameId: str,targetAgent: str,targetTeam: str= None) -> dict:
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
    _save_json(matchData,jsonName= "get_last_match_agent_data_old_game")
    if(len(matchData['data']) == 0):
       print(f"{errorCode.ERR_CODE_101} - No recent games found for the user, even using v2 API")
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
        print(f"{errorCode.ERR_CODE_103} - No player was using {targetAgent} in the last game of {name}")
        return errorCode.ERR_CODE_103
    else:
        #Get data of the desired player
        region = matchData['data']['metadata']['region']
        target_elo = get_this_season_elo(region= region,name= targetData['name'], tag= targetData['tag'])
        target_HS = get_last_match_HS_percentage(region= region, name= targetData['name'], tag= targetData['tag'])
        if(errorCode.isErrorCode(target_elo) == True):
            return target_elo #Return error code
        elif(errorCode.isErrorCode(target_HS) == True):
            return target_HS #Return error code
        else:
            result = {'elo': target_elo, 'HS': target_HS, 'name': targetData['name']}
            return result

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
    #To Do: investigate bug when match is not ranked or unranked
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

def get_player_data(player: str) -> dict:
    """
        Get Valorant user data depending on Discord user data.

        Parameters:
            player  (str):  Discord user name
        Returns:
            Response: Dictionary with the player region, name and tag.
        """
    #To Do: Implement this in private json for privacy reasons
    #To Do: Add puuid to the dictionary for every player
    #To Do: Move tokens to a folder private/
    alvaro = {'region': 'eu', 'name': 'SpaguettiCoded', 'tag': "EUW"}
    dani = {'region': 'eu', 'name': 'Barl0ck', 'tag': "0205"}
    ana = {'region': 'eu', 'name': 'shadowdanna', 'tag': "81502"}
    laura = {'region': 'eu', 'name': 'nightdise', 'tag': "EUW"}

    alvaro_discord = "luzil19"
    dani_discord = "barlock3"
    ana_discord = "anitta9573"
    laura_discord = "nightdise"

    user = str(player)
    if(user == alvaro_discord):
        return alvaro
    elif(user == dani_discord):
        return dani
    elif(user == ana_discord):
        return ana
    elif(user == laura_discord):
        return laura
    else:
        print(f"{errorCode.ERR_CODE_120}Wrong discord user name")
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
    targetStandard = target.capitalize()
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
            print(f"{errorCode.ERR_CODE_121} - Target not found in map nor in agent lists")
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
       print(f"{errorCode.ERR_CODE_107} - Mariano played no matches")
       return errorCode.ERR_CODE_107
    mariano_lost_percentage = (mariano_lost/(mariano_lost + mariano_won)) * 100
    return round(mariano_lost_percentage,2)

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
        print(f"{errorCode.ERR_CODE_101} - No recent game found for the user")
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
        print(f"{errorCode.ERR_CODE_121} - Target not found in map nor in agent lists")
        return errorCode.ERR_CODE_121
    
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
                print(f"{errorCode.ERR_CODE_101} - No recent games found for the user")
                return errorCode.ERR_CODE_101
            gameData = matchData['data'][0]['players']['all_players']
        elif(jsonVersion.lower() == "v2"):
            gameData = matchData['data']['players']['all_players']
        else:
            print(f"{errorCode.ERR_CODE_110} - Requested JSON version is not valid")
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
                print(f"{errorCode.ERR_CODE_101} - No recent games found for the user")
                return errorCode.ERR_CODE_101
            gameData = matchData['data'][0]['players'][team]
        elif(jsonVersion.lower() == "v2"):
            gameData = matchData['data']['players'][team]
        else:
            print(f"{errorCode.ERR_CODE_110} - Requested JSON version is not valid")
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
       print(f"{errorCode.ERR_CODE_106} - No matches with the selected agent")
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
       print(f"{errorCode.ERR_CODE_105} - No matches in the selected map")
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
        print(f"{errorCode.ERR_CODE_101} - No recent games found for the user")
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
    #To Do: investigate bug when match is not ranked or unranked
    #Get last match data
    elo_request = api.get_this_season_elo_api(region= region,name= name,tag= tag)
    #Parse data
    eloData = elo_request.json()
    _save_json(eloData,jsonName= "_get_elo")

    #Check if player has changed its name
    if(eloData['status'] != 200):   #To Do: add this check to every API call
        print(f"{errorCode.ERR_CODE_104} - API returned error code {eloData['status']}")
        return errorCode.ERR_CODE_104

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
       print(f"{errorCode.ERR_CODE_101} - No recent games found for the user")
       return None
    else:
        game_id = matchData['data'][0]['meta']['id']
        return game_id

def main():
    name = "nightdise"
    region = "eu"
    tag = "EUW"
    target = "Omen"
    result = get_avg_elo(name= name, region= region, tag= tag)
    print(result)

if __name__ == "__main__":
    main()
