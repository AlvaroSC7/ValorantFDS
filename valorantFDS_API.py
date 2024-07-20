import requests
from PiumPiumBot_Config import PiumPiumBot_Config

# To Do: Investigar v4 API


class ValorantFDS_API:
    def __init__(self):
        self.general_url = "https://api.henrikdev.xyz/valorant/"

    def get_lifetime_matches(self, region: str, name: str, tag: str, mode: str = None, map: str = None, page: int = None, size: int = None):
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
        return self._send_request(url, params)

    def get_lifetime_matches_by_matchId(self, matchId: str):
        """
        Get Valorant lifetime matches stat for a player.

        Parameters:
            matchId  (str):  MatchID.
        Returns:
            Response: The HTTP response containing the game data.
        """

        url = self.general_url + f"v2/match/{matchId}"
        return self._send_request(url)

    def get_v3_matches(self, region: str, name: str, tag: str):
        """
        Get Valorant last match of a player in detail.

        Parameters:
            region  (str):  The Valorant region.
            name    (str):  The player name.
            tag     (str):  The player tag.
        Returns:
            Response: The HTTP response containing the last match data in detail.
        """

        url = self.general_url + f"v3/matches/{region}/{name}/{tag}"
        return self._send_request(url)

    def get_content(self, locale: str = None):
        """
        Get all Valorant native content (maps, agents, skins etc...).

        Parameters:
            locale  (str):  The Valorant language. Optional
        Returns:
            Response: The HTTP response containing the content.
        """

        url = self.general_url + "v1/content"
        params = {'locale': locale}
        return self._send_request(url, params= params)

    def get_esports_schedule(self, region: str = None, league: str = None):
        """
        Get all esports competitions information.

        Parameters:
            region  (str):  Region of the esport match or competition. Optional
            league  (str):  Competition itself. Optional
        Returns:
            Response: The HTTP response containing the content.
        """

        url = self.general_url + "v1/esports/schedule"
        params = {'region': region, 'league': league}
        return self._send_request(url, params= params)

    def get_this_season_elo_api(self, region: str, name: str, tag: str):
        """
        Get player elo in the active season

        Parameters:
            region  (str):  The Valorant region.
            name    (str):  The player name.
            tag     (str):  The player tag.
        Returns:
            Response: The player elo in the current season
        """

        url = self.general_url + f"v1/mmr/{region}/{name}/{tag}"
        return self._send_request(url)

    def get_by_puuid_mmr_v2(self, region: str, puuid: str, season: str = None):
        """
        Get player elo in every season using puuid as input

        Parameters:
            region  (str):  The Valorant region.
            puuid   (str):  The player puuid.
            season  (str):  Season where to look the elo. Optional.
        Returns:
            Response: The player elo in every season or in the one selected
        """

        url = self.general_url + f"v2/by-puuid/mmr/{region}/{puuid}"
        params = {'season': season}
        return self._send_request(url, params= params)

    def _get_api_key(self):
        """
        Get API Key to be used in any request. It must be stored in ValorantAPIKey.txt

        Parameters:
            void

        Returns:
            Response: API Key.
        """
        config = PiumPiumBot_Config()
        path = config.PRIVATE_PATH + "/ValorantAPIKey.txt"
        apiKeyFile = open(path, "r")
        apiKey = apiKeyFile.read()
        return apiKey

    def _send_request(self, url: str, params: str = None):
        """
        Send request to the given url

        Parameters:
            url     (str):  URL where the petition will be sent
            params  (str):  optional parameters for the request. Ignored if not given

        Returns:
            Response: API Response.
        """
        api_key = self._get_api_key()
        headers = {
            "Authorization": api_key,
        }

        try:
            response = requests.get(url, headers=headers, params= params)
            response.raise_for_status()
            return response
        except requests.exceptions.HTTPError as http_err:
            print(f"HTTP Error retrieving matches: {http_err}")
            return http_err.response
        except requests.exceptions.RequestException as req_err:
            print(f"Error retrieving matches: {req_err}")
            return None


class vlrgg_API:
    def __init__(self):
        self.general_url = "https://vlrggapi.vercel.app/"

    def get_matches(self, matchStatus: str):
        """
        Get past, live or upcoming matches information from vlr.gg.

        Parameters:
            matchStatus (str):  Type of match to fetch: upcoming, live_score or results
        Returns:
            Response: The HTTP response containing the content.
        """

        url = "https://vlrggapi.vercel.app/" + "match"
        params = {'q': matchStatus}
        return self._send_request(url, params= params)

    def _send_request(self, url: str, params: str = None):
        """
        Send request to the given url

        Parameters:
            url     (str):  URL where the petition will be sent
            params  (str):  optional parameters for the request. Ignored if not given

        Returns:
            Response: API Response.
        """

        try:
            response = requests.get(url, params= params)
            response.raise_for_status()
            return response
        except requests.exceptions.HTTPError as http_err:
            print(f"HTTP Error retrieving matches: {http_err}")
            return http_err.response
        except requests.exceptions.RequestException as req_err:
            print(f"Error retrieving matches: {req_err}")
            return None
