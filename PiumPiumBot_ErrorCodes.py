from re import findall, search
import inspect
import logging

logger = logging.getLogger(__name__)

class ErrorCodes:
    def __init__(self):
        #Errors related to lack of data provided by the API 
        self.ERR_CODE_100 = "ERR_CODE_100"  #Player changed its name or tag since the last game
        self.ERR_CODE_101 = "ERR_CODE_101"  #No recent matches found for the user
        self.ERR_CODE_102 = "ERR_CODE_102"  #Player not found in last game
        self.ERR_CODE_103 = "ERR_CODE_103"  #No player found using the target agent in the last user game
        self.ERR_CODE_104 = "ERR_CODE_104"  #Esport team has no upcoming/played games data
        self.ERR_CODE_105 = "ERR_CODE_105"  #No recent matches found for the user in the selected map
        self.ERR_CODE_106 = "ERR_CODE_106"  #No recent matches found for the user with the selected agent
        self.ERR_CODE_107 = "ERR_CODE_107"  #No recent games found, even using v2 API
        self.ERR_CODE_108 = "ERR_CODE_108"  #No available agents in the roulette pool
        self.ERR_CODE_109 = "ERR_CODE_109"
        #Internal errors
        self.ERR_CODE_110 = "ERR_CODE_110"  #Wrong Json version used in internal function. ie, v2 API Json used in v3 function
        self.ERR_CODE_111 = "ERR_CODE_111"  #Competition unknown for esports command
        self.ERR_CODE_112 = "ERR_CODE_112"  #Esport team is unkwnown for esports command
        self.ERR_CODE_113 = "ERR_CODE_113"  #Internal bot files missing
        self.ERR_CODE_114 = "ERR_CODE_114"
        self.ERR_CODE_115 = "ERR_CODE_115"
        self.ERR_CODE_116 = "ERR_CODE_116"
        self.ERR_CODE_117 = "ERR_CODE_117"
        self.ERR_CODE_118 = "ERR_CODE_118"
        self.ERR_CODE_119 = "ERR_CODE_119"
        #Discord related errors
        self.ERR_CODE_120 = "ERR_CODE_120"  #Wrong discord user name
        self.ERR_CODE_121 = "ERR_CODE_121"  #Selected agent or map do not exist
        self.ERR_CODE_122 = "ERR_CODE_122"  #No input parameter given. No map or agent selected for a command that required it
        self.ERR_CODE_123 = "ERR_CODE_123"  #Wrong team name
        self.ERR_CODE_124 = "ERR_CODE_124"  #Map selected when agent or player name was expected
        self.ERR_CODE_125 = "ERR_CODE_125"  #Wrong parameter in roulette
        self.ERR_CODE_126 = "ERR_CODE_126"
        self.ERR_CODE_127 = "ERR_CODE_127"
        self.ERR_CODE_128 = "ERR_CODE_128"
        self.ERR_CODE_129 = "ERR_CODE_129"
        #Unknown error
        self.ERR_CODE_199 = "ERR_CODE_199"

    def isErrorCode(self, errorCode) -> bool:
        """
            This function checks the response of any valorantFDS function and returns whether it is an error code or not.

            Parameters:
                errorCode   (str):  value returned by the valorantFDS function
            Returns:
                Response: True if input parameters is an error code, False otherwise
            """
        if(type(errorCode) != str): #If it is not a string it is an internal value properly returned
            return False
        else:
            #Check if the string is any error code
            isError = search("^ERR_CODE_([0-9]){3,5}", errorCode)
            if(isError != None):
                return True 
            else:
                return False

    def handleErrorCode(self, errorCode: str, httpError: str= None) -> str:
        """
            This function checks the response of any valorantFDS function and converts any error code into it's meaning so bot user can understand it.

            Parameters:
                errorCode   (str):  value returned by the valorantFDS function
                httpError   (str):  HTTP error if it needs to be printed. OPTIONAL, just for some error codes
            Returns:
                Response: Meaning of the error code, to be understood by the Discord user. None if there is no error
            """
        if(type(errorCode) != str):
            return None #Not a string, probably an internal function returning other type normally

        #Check if the string is any error code
        errorCodeGroup = findall("(?<=^ERR_CODE_1)(.*)(?=[0-9])", errorCode)
        if(errorCodeGroup == []):
            return None #Not an error code. Return None to indicate it
        else:
            return self._callErrorGroup(errorCode= errorCode, errorCodeGroup= errorCodeGroup[0])

    def _callErrorGroup(self, errorCode: str, errorCodeGroup: str):
        if(errorCodeGroup == "0"):  #Errors related to lack of data provided by the API
            result = self._errorGroupNoDataAPI(errorCode= errorCode)
        elif(errorCodeGroup == "1"):  #Errors related to internal behaviour or code related issues
            result = self._errorGroupInternal(errorCode= errorCode)
        elif(errorCodeGroup == "2"):  #Errors related to Discord
            result = self._errorGroupDiscord(errorCode= errorCode)
        else:
            result = self._errorUnknownError()
        return result

    def _errorGroupNoDataAPI(self, errorCode: str, httpError: str= None) ->str:
        curframe = inspect.currentframe()
        calframe = inspect.getouterframes(curframe, 4)

        if(errorCode == self.ERR_CODE_100):
            result = "El jugador ha cambiado su nombre o tag desde tu última partida con el"
            logMessage = f"{calframe[3][3]}: {errorCode} - API returned error code {httpError}"
        elif(errorCode == self.ERR_CODE_101):
            result = "No se han encontrado partidas recientes"
            logMessage = f"{calframe[3][3]}: {errorCode} - No recent games found for the user"
        elif(errorCode == self.ERR_CODE_102):
            result = "No se ha encontrado al jugador objetivo en tu anterior partida"
            logMessage = f"{calframe[3][3]}: {errorCode} - Player not found in last game"
        elif(errorCode == self.ERR_CODE_103):
            result = "No se ha encontrado ningun jugador usando el agente objetivo en tu ultima partida"
            logMessage = f"{calframe[3][3]}: {errorCode} - No player was using the selected agent in the user's last game"
        elif(errorCode == self.ERR_CODE_104):
            result = "El equipo seleccionado no tiene partidos proximos o resultados conocidos para esta competicion"
            logMessage = f"{calframe[3][3]}: {errorCode} - Requested team has not played or upcoming matches data"
        elif(errorCode == self.ERR_CODE_105):
            result = "No hay registradas partidas recientes en el mapa seleccionado"
            logMessage = f"{calframe[3][3]}: {errorCode} - No matches in the selected map"
        elif(errorCode == self.ERR_CODE_106):
            result = "No hay registradas partidas recientes con el agente seleccionado"
            logMessage = f"{calframe[3][3]}: {errorCode} - No matches with the selected agent"
        elif(errorCode == self.ERR_CODE_107):
            result = "No se han encontrado partidas recientes, incluso buscando en los datos mas antiguos"
            logMessage = f"{calframe[3][3]}: {errorCode} - Player not found in last game, even using v2 API"
        elif(errorCode == self.ERR_CODE_108):
            result = "No quedan agentes disponibles, se ha resetado la ruleta, vuelve a ejecutar el comando. Se recomienda ejecutar !ruleta reset tras completar un equipo"
            logMessage = f"{calframe[3][3]}: {errorCode} - No remaining agents in the roulette pool"
        else:
            result = self._errorUnknownError()

        print(logMessage)
        logger.warning(logMessage)
        return result

    def _errorGroupInternal(self, errorCode: str) ->str:
        curframe = inspect.currentframe()
        calframe = inspect.getouterframes(curframe, 4)

        if(errorCode == self.ERR_CODE_110):
            result = "Error interno, version de Json file erronea"
            logMessage = f"{calframe[3][3]}: {errorCode} - Requested JSON version is not valid"
        elif(errorCode == self.ERR_CODE_111):
            result = "Error interno, competicion desconocida"
            logMessage = f"{calframe[3][3]}: {errorCode} - Requested competition for esport command is unknown"
        elif(errorCode == self.ERR_CODE_112):
            result = "Error interno, equipo desconocido"
            logMessage = f"{calframe[3][3]}: {errorCode} - Requested team is not known for esport command"
        elif(errorCode == self.ERR_CODE_113):
            result = "No se han encontrado datos de ningun usuario guardados. Para mas informacion sobre como configurar tus datos en el bot usa !help user"
            logMessage = f"{calframe[3][3]}: {errorCode} - Internal data file missing"
        else:
            result = self._errorUnknownError()

        print(logMessage)
        logger.warning(logMessage)
        return result

    def _errorGroupDiscord(self, errorCode: str) ->str:
        curframe = inspect.currentframe()
        calframe = inspect.getouterframes(curframe, 4)

        if(errorCode == self.ERR_CODE_120):
            result = "Este usuario de Discord no tiene datos de Valorant registrados"
            logMessage = f"{calframe[3][3]}: {errorCode} - Wrong discord user name"
        elif(errorCode == self.ERR_CODE_121):
            result = "No se ha reconocido el agente o mapa especificado"
            logMessage = f"{calframe[3][3]}: {errorCode} - Target not found in map nor in agent lists"
        elif(errorCode == self.ERR_CODE_122):
            result = "Faltan parametros de entrada para el comando. Ejemplo: !last_game shadowdanna | !last_game Reyna | !wr Abyss"
            logMessage = f"{calframe[3][3]}: {errorCode} - No target player given"
        elif(errorCode == self.ERR_CODE_123):
            result = "Nombre de equipo incorrecto. Posibles valores: enemy | ally . Si no introduces ninguno se mirara primero en los enemigos y luego en los aliados. Si querias poner un nombre con espacios usa \" \". Ejemplo: !last_game \"Un nombre\""
            logMessage = f"{calframe[3][3]}: {errorCode} - Wrong team name"
        elif(errorCode == self.ERR_CODE_124):
            result = "Has seleccionado un mapa. Selecciona un nombre de jugador o de agente para revisar sus datos. Ejemplo: !last_game shadowdanna | !peak Reyna"
            logMessage = f"{calframe[3][3]}: {errorCode} - Map selected when agent or player ID was expected"
        elif(errorCode == self.ERR_CODE_125):
            result = "Parametro inesperado. Para tirar la ruleta usa !ruleta. Para resetear la ruleta usa !ruleta reset"
            logMessage = f"{calframe[3][3]}: {errorCode} - Wrong roulette parameter"
        else:
            result = self._errorUnknownError()

        print(logMessage)
        logger.warning(logMessage)
        return result

    def _errorUnknownError(self)-> str:
        curframe = inspect.currentframe()
        calframe = inspect.getouterframes(curframe, 5)
        logMessage = f"{calframe[3][3]}: {self.ERR_CODE_199} - Unknown error"
        print(logMessage)
        logger.warning(logMessage)
        return "Error desconocido"
    