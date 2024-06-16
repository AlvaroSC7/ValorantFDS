import sys
from valo_api import set_api_key
import requests
import json

def get_leaderboard(region: str):
    """
    Get Valorant leaderboard information.

    Parameters:
        region (str): The Valorant region.

    Returns:
        Response: The HTTP response containing leaderboard information.
    """

    url = f"https://api.henrikdev.xyz/valorant/v1/leaderboard/{region}"
    api_key = get_api_key()
    headers = {
        "Authorization": api_key,
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response
    except requests.exceptions.HTTPError as http_err:
        return http_err.response
    except requests.exceptions.RequestException as req_err:
        print(f"Error retrieving Valorant leaderboard information: {req_err}")
        return None
    
def get_api_key():
    """
    Get API Key to be used in any request.

    Parameters:
        void

    Returns:
        Response: API Key.
    """
    return "HDEV-d7772cbc-223c-4593-8cb6-2345e30f3de3"  #To Do: read this from file for privacy reasons)

def main():
    #name = "SpaguettiCoded"
    #tag = "EUW"
    #version = "08.11.00.2606987" 
    leaderboard_request = get_leaderboard(region="na")
    jsonArchive = leaderboard_request.json()
    with open ("archivo.json","w") as j:
        json.dump(jsonArchive,j)

if __name__ == "__main__":
    main()
