from discord.ext import commands
import json
from PiumPiumBot_Config import PiumPiumBot_Config
from PiumPiumBot_ErrorCodes import ErrorCodes

config = PiumPiumBot_Config()
errorCode = ErrorCodes()

class InternalCommands(commands.Cog):
    "Comandos para la configuracion del bot y obtencion de informacion del mismo"

    ##################################################################
    #                         COMMANDS                               #
    ##################################################################

    @commands.command(name='version')
    async def get_version(self, ctx):
        "Version de PiumPiumBot que se esta ejecutando"
        response = f"{config.version}-{config.type[0]}"
        await ctx.send(response)

    @commands.command(name='host')
    async def get_host(self, ctx):
        "Informacion del host y servidor donde PiumPiumBot está alojado actualmente"
        response = f"URL: {config.host.url}\nID: {config.host.id}\nNode: {config.host.node}"
        await ctx.send(response)

    @commands.command(name='user')
    async def save_user(self, ctx, 
                        name: str = commands.parameter(default=None, description="Nombre de usuario de Valorant"), 
                        tag: str = commands.parameter(default=None, description="Tag de Valorant"), 
                        region: str = commands.parameter(default="eu", description="Region donde juegas. Posibles valores: ap, br, eu, kr, latam, na")):
         
        "Guarda los datos de un jugador en la configuracion interna de PiumPium. Necesario para que la mayoria de los comandos funcione"
        author = str(ctx.message.author)
        response = self._store_data(discord= author, name= name, tag= tag, region= region)
        await ctx.send(response)

    @commands.command(name='del')
    async def delete_user(self, ctx):
        "Borra los datos de un jugador en la configuracion interna de PiumPium. Es recomendable usarlo si se va a dejar un servidor en el que has usado el bot previamente"
        author = str(ctx.message.author)
        response = self._remove_data(discord= author)
        await ctx.send(response)

    ##################################################################
    #                    INTERNAL FUNCTIONS                          #
    ##################################################################

    def _store_data(self, discord: str, name: str, tag: str, region: str= "eu") -> str:
        """
            Save Valorant user data in the bot internal files.

            Parameters:
                discord (str):  Discord user name
                name    (str):  Valorant user name
                tag     (str):  Valorant user tag
                region  (str):  Valorant user region. If it is not provided eu is selected as default
            Returns:
                Response: String with the confirmation (or error message) of the data storage.
            """
        #To Do: Add puuid to the dictionary for every player once it is stored in Json so puuid is only looked once. Improves performance

        gameData = {'region': region, 'name': name, 'tag': tag}
        newUser = {'discord': str(discord), 'gameData': gameData}  

        usersFile = config.PRIVATE_PATH + '/userList.json'
        response = f"Datos de {str(discord)} guardados"
        #If file exist modify user data or add it if it is a new user
        try:
            with open(usersFile) as json_file:
                userList = json.load(json_file)

            userAlreadyStored = False
            for user in userList['user']:
                if(user['discord'] == str(discord)):
                    user['gameData'] = gameData  #User already stored, overwrite his data
                    userAlreadyStored = True
                    response = f"Ya habia datos de {user['discord']}, se han sobreescrito los datos"
            if(userAlreadyStored == False):
                userList['user'].append(newUser)    #User is not stored, add his data
        #If it is the first time the bot is used in the server create the user list
        except:
            userList = {'user': [newUser]}

        usersJson = json.dumps(userList, indent=4)
        with open (usersFile,"w") as f:
            f.write(usersJson)
            f.truncate()
        return response

    def _remove_data(self, discord: str) -> str:
        """
        Remove a Valorant user data in the bot internal files.
        Parameters:
            discord (str):  Discord user name
        Returns:
            Response: String with the confirmation (or error message) of the data removal.
        """
        usersFile = config.PRIVATE_PATH + '/userList.json'
        try:
            with open(usersFile) as json_file:
                userList = json.load(json_file)
        except:
            return errorCode.handleErrorCode(errorCode.ERR_CODE_113)
        response = f"No se han encontrado datos de {discord}"
        for user in userList['user']:
            if(user['discord'] == str(discord)):
                userList['user'].remove(user)
                response = f"Los datos sobre {discord} se han borrado correctamente"
                break
        usersJson = json.dumps(userList, indent=4)
        with open (usersFile,"w") as f:
            f.write(usersJson)
            f.truncate()
        return response