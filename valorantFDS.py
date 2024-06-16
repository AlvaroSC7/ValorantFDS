import sys
from valo_api import set_api_key
import requests
import json
from os.path import dirname, abspath

general_url = "https://api.henrikdev.xyz/valorant/"

def get_lifetime_matches(region: str,name: str,tag: str,mode: str=None,map: str=None,page: int=None,size: int=None):
    """
    Get Valorant lifetime matches stat for a player.

    Parameters:
        region  (str):  The Valorant region.
        name    (str):  The player name.
        tag     (str):  The player tag.
        mode    (str):  Game mode of the matches. Options: competitive unrated deathmatch ... OPTIONAL
        map     (str):  The map name. Starts with capital letters. OPTIONAL
        page    (int):  Page size used for indentation. OPTIONAL
        size    (int):  Number of returned matches. OPTIONAL 
    Returns:
        Response: The HTTP response containing the player matches.
    """

    url = general_url + f"v1/lifetime/matches/{region}/{name}/{tag}"
    params = {'mode': mode, 'map': map, 'page': page, 'size': size}
    api_key = get_api_key()
    headers = {
        "Authorization": api_key,
    }

    try:
        response = requests.get(url, headers=headers,params=params)
        response.raise_for_status()
        return response
    except requests.exceptions.HTTPError as http_err:
        return http_err.response
    except requests.exceptions.RequestException as req_err:
        print(f"Error retrieving matches: {req_err}")
        return None
    
def get_api_key():
    """
    Get API Key to be used in any request. It must be stored in ValorantAPIKey.txt

    Parameters:
        void

    Returns:
        Response: API Key.
    """
    ws_path = dirname(abspath(__file__))
    path = ws_path + "/ValorantAPIKey.txt"
    apiKeyFile = open(path,"r")
    apiKey = apiKeyFile.read()
    return apiKey

def main():
    name = "SpaguettiCoded"
    tag = "EUW"
    matches_request = get_lifetime_matches(region="eu",name=name,tag=tag)
    print(matches_request)
    print(matches_request.url)
    jsonArchive = matches_request.json()
    with open ("archivo.json","w") as j:
        json.dump(jsonArchive,j)

if __name__ == "__main__":
    main()
