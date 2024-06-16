import requests
from os.path import dirname, abspath

class ValorantFDS_API:
    def __init__(self):
        self.general_url = "https://api.henrikdev.xyz/valorant/"

    def get_lifetime_matches(self,region: str,name: str,tag: str,mode: str=None,map: str=None,page: int=None,size: int=None):
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

        url = self.general_url + f"v1/lifetime/matches/{region}/{name}/{tag}"
        params = {'mode': mode, 'map': map, 'page': page, 'size': size}
        api_key = self._get_api_key()
        headers = {
            "Authorization": api_key,
        }

        try:
            response = requests.get(url, headers=headers,params=params)
            response.raise_for_status()
            return response
        except requests.exceptions.HTTPError as http_err:
            print(f"HTTP Error retrieving matches: {http_err}")
            return http_err.response
        except requests.exceptions.RequestException as req_err:
            print(f"Error retrieving matches: {req_err}")
            return None

    def _get_api_key(self):
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
