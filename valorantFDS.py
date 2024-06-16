import json
from valorantFDS_API import ValorantFDS_API

api = ValorantFDS_API()

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
    matches_request = api.get_lifetime_matches(region="eu",name=name,tag=tag,size=1)
    #Parse data
    matchData = matches_request.json()
    with open ("archivo.json","w") as j:
        json.dump(matchData,j)
    headshots = matchData['data'][0]['stats']['shots']['head']
    total_shots = headshots + matchData['data'][0]['stats']['shots']['body'] + matchData['data'][0]['stats']['shots']['leg']
    #Calculate accuracy
    HS_accuracy = (headshots/total_shots) * 100
    return round(HS_accuracy,2)

def get_player_data(player: str) -> dict:
    """
        Get Valorant user data depending on Discord user data.

        Parameters:
            player  (str):  Discord user name
        Returns:
            Response: Dictionary with the player region, name and tag.
        """
    
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


def get_mariano_lost_percentage() -> float:
    mariano = {'region': 'eu', 'name': 'Mariano', 'tag': "455"}
    #Get last match data
    matches_request = api.get_lifetime_matches(region= mariano['region'],name= mariano['name'],tag= mariano['tag'])
    #Parse data
    matchData = matches_request.json()
    with open ("archivo.json","w") as j:
        json.dump(matchData,j)
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
    mariano_lost_percentage = (mariano_lost/(mariano_lost + mariano_won)) * 100
    return round(mariano_lost_percentage,2)



def main():
    mariano_percentage = get_mariano_lost_percentage()
    print(mariano_percentage)

if __name__ == "__main__":
    main()
