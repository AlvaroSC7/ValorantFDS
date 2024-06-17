import json
from valorantFDS_API import ValorantFDS_API
from PiumPiumBot_Config import PiumPiumBot_Config

api = ValorantFDS_API()
bot = PiumPiumBot_Config()

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
    headshots = matchData['data'][0]['stats']['shots']['head']
    total_shots = headshots + matchData['data'][0]['stats']['shots']['body'] + matchData['data'][0]['stats']['shots']['leg']
    #Calculate accuracy
    HS_accuracy = (headshots/total_shots) * 100
    return round(HS_accuracy,2)

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
    for player in matchData['data'][0]['players']['all_players']:
        if(str(player['name']) == targetName):
            playerName = str(player['name'])
            playerTag = str(player['tag'])
            playerFound = True
            break
    
    if(playerFound == False):
        print("Error - Player not found in last game")
        return None
    else:
        #Get data of the desired player
        player_elo = get_this_season_elo(region= region,name= playerName, tag= playerTag)
        player_HS = get_last_match_HS_percentage(region= region, name= playerName, tag= playerTag)
        result = {'elo': player_elo, 'HS': player_HS}
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
    
    #Get last match data
    elo_request = api.get_this_season_elo_api(region= region,name= name,tag= tag)
    #Parse data
    eloData = elo_request.json()
    _save_json(eloData,jsonName= "get_this_season_elo")
    
    result = eloData['data']['currenttierpatched'] + " - " + str(eloData['data']['elo'])
    
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
    alvaro = {'region': 'eu', 'name': 'SpaguettiCoded', 'tag': "EUW"}
    dani = {'region': 'eu', 'name': 'Barl0ck', 'tag': "0205"}
    ana = {'region': 'eu', 'name': 'shadowdanna', 'tag': "81502"}
    laura = {'region': 'eu', 'name': 'nightdise', 'tag': "EUW"}
    error_dict = {}

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
        print("Wrong discord user name")
        return error_dict
    
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
        print("Error - Target not found in map nor in agent lists")
        return None
    
    return targetType

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
    if(targetType == None):
        print("Error - Not a known agent or map")
        return None
    else:
        #Get liffetime match data
        if(targetType == "map"):
            targetWR = _get_map_wr(region= region,name= name,tag= tag,map= targetStandard)
        elif(targetType == "agent"):
            targetWR = _get_agent_wr(region= region,name= name,tag= tag,agent= targetStandard)
        else:
            print("Error - Not a known map or agent")
            return None

        return targetWR

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
       print("Error - No matches in the selected map")
       return None
    map_wr = (wonMatches/(wonMatches + lostMatches)) * 100
    return round(map_wr,2)

#To Do: IMPLEMENT
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
    #matches_request = api.get_lifetime_matches(region= region,name= name,tag= tag,= targetStandard) #For agents v3/matches is needed
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
       print("Error - No matches with the selected agent")
       return None
    agent_wr = (wonMatches/(wonMatches + lostMatches)) * 100
    return round(agent_wr,2)


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
       print("Error - Mariano played no matches")
       return None
    mariano_lost_percentage = (mariano_lost/(mariano_lost + mariano_won)) * 100
    return round(mariano_lost_percentage,2)

def _save_json(data,jsonName: str):
    if(bot.type == "DEV"):
        with open (bot.TEMP_PATH + "/" + jsonName + ".json","w") as j:
            json.dump(data,j)



def main():
    name = "SpaguettiCoded"
    region = "eu"
    tag = "EUW"
    target = "Omen"
    map_wr = _get_agent_wr(name= name, region= region, tag= tag,agent= target)
    print(f"WR with {target}: {map_wr}%")

if __name__ == "__main__":
    main()
