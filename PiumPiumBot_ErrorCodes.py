from re import match

elif(function == handleErrorCode(errorCode: str, function: str) -> str:
    """
        This function checks the response of any valorantFDS function and converts any error code into it's meaning so bot user can understand it.

        Parameters:
            errorCode   (str):  value returned by the valorantFDS function
            function    (str):  Function that returned the given potential error code
        Returns:
            Response: Meaning of the error code, to be understood by the Discord user. None if there is no error
        """
    #Check if the string is any error code
    isErrorCode = match("^ERR_CODE_[0-9]{3,5}", errorCode)
    if(isErrorCode == None):
        return None #Not an error code. Return None to indicate it
    else:
        return translateErrorCode(errorCode= errorCode, function= function)
    
def translateErrorCode(errorCode: str, function: str) -> str:
    """
        This function checks the response of any valorantFDS function and converts any error code into it's meaning so bot user can understand it.

        Parameters:
            errorCode   (str):  value returned by the valorantFDS function
            function    (str):  Function that returned the given potential error code
        Returns:
            Response: Meaning of the error code, to be understood by the Discord user
        """
    #Check which function is it
    if(function == "get_last_match_HS_percentage"):
    
    
    elif(function == "_get_last_match_ID"):
        
    
    elif(function == "get_last_match_player_data"):
        
        
    elif(function == "get_last_match_player_data_old_game"):
        
    elif(function == "_get_player_and_opposite_team"):
            
    
    elif(function == "_extract_player_data_with_agent_and_team"):
        
        
    elif(function == "get_last_match_agent_data"):
        
    elif(function == "get_last_match_agent_data_old_game"):
        
    elif(function == "get_this_season_elo"):
        
    
    elif(function == "get_player_data"):
        
    elif(function == "_get_target_type"):
        
    elif(function == "get_target_wr"):
        
    elif(function == "_get_map_wr"):
        
    elif(function == "_get_agent_wr"):
        
    elif(function == "get_mariano_lost_percentage"):
    