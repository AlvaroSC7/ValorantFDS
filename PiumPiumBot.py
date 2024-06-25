import discord
from discord.ext import commands
from os.path import dirname, abspath
from valorantFDS import get_last_match_HS_percentage, get_player_data, get_mariano_lost_percentage, get_this_season_elo, get_target_wr, get_avg_elo, peak_elo, get_last_match_data
from PiumPiumBot_ErrorCodes import ErrorCodes
from PiumPiumBot_Config import PiumPiumBot_Config

def get_bot_token():
    """
    Get Discord bot token to be used in any request. It must be stored in PiumPiumToken.txt

    Parameters:
        void

    Returns:
        Response: Bot token.
    """
    ws_path = dirname(abspath(__file__))
    path = ws_path + "/PiumPiumToken.txt"
    tokenFile = open(path,"r")
    token = tokenFile.read()
    return token

intents = discord.Intents.all()
helper = commands.DefaultHelpCommand(width= 500, no_category = 'Comandos disponibles')
bot = commands.Bot(command_prefix='!',intents=intents, help_command= helper)
errorCodeList = ErrorCodes()
config = PiumPiumBot_Config()

##################################################################
#                         COMMANDS                               #
##################################################################
#To Do: comando sens
#To Do: comando para setear datos de jugadores
#To Do: comando para obtener mira
#To Do: comando sonido ace
#To Do: comando acs last game
#To Do: comando que implemente bug ticket. Envia un correo a mi email, que se saca de un txt privado
#To Do: Implement !esports !vct !masters
#To Do: Implement !host to return where the answering bot is running

#To Do: borrar esta funcion cuando ya nadie la use
@bot.command(name='HS')
async def get_HS_percentage_deprecate(ctx):
    """ 
        Indica el porcentaje de tiros a la cabeza que has tenido en tu ultima partida

        !HS no esta continuado y se eliminará en futuras versiones en favor de !hs, considera usar ya el nuevo comando
        """
    await get_HS_percentage(ctx)
    response = f"!HS no esta continuado y se eliminará en futuras versiones en favor de !hs, considera usar ya el nuevo comando"
    await ctx.send(response)

@bot.command(name='hs')
async def get_HS_percentage(ctx):
    "Indica el porcentaje de tiros a la cabeza que has tenido en tu ultima partida"
    author = ctx.message.author
    player = get_player_data(player=author)
    errorCode = errorCodeList.handleErrorCode(player)
    if(errorCode != None):
        await ctx.send(errorCode)
    else:
        HS_accuracy = get_last_match_HS_percentage(region= player['region'], name= player['name'], tag= player['tag'])
        errorCode = errorCodeList.handleErrorCode(HS_accuracy)
        if(errorCode != None):
            await ctx.send(errorCode)
        else:
            response = f"Tu precision en la ultima partida fue: {HS_accuracy}%"
            await ctx.send(response)

@bot.command(name='elo')
async def get_elo(ctx):
    "Indica tu elo actual como {Rango} - {Puntuacion total en el sistema de rangos}"
    author = ctx.message.author
    player = get_player_data(player=author)
    errorCode = errorCodeList.handleErrorCode(player)
    if(errorCode != None):
        response = errorCode
    else:
        elo = get_this_season_elo(region= player['region'], name= player['name'], tag= player['tag'])
        errorCode = errorCodeList.handleErrorCode(elo)
        if(errorCode != None):
            response = errorCode
        else:
            response = elo

    await ctx.send(response)

#To Do: borrar esta funcion cuando ya nadie la use
@bot.command(name='last_game')
async def get_last_game_player_data_deprecate(ctx,
                                              target_player: str = commands.parameter(default=None, description="nombre o agente del jugador cuyos datos quieres saber"), 
                                              target_team: str= commands.parameter(default=None, description="OPCIONAL. Equipo donde quieres buscar al agente en cuestion (ally/enemy). No necesario en caso de busqueda por nombre. Si no se especifica y el mismo agente se jugo en ambos equipos se da por defecto el jugador rival")):
    """
        Proporciona el elo y porcentaje de tiro a la cabeza de cualquier jugador de tu ultima partida
        
        Ejemplos: !lg IMissHer !lg Sova enemy !lg Jett"
        
        !last_game no esta continuado y se eliminará en futuras versiones en favor de !lg, considera usar ya el nuevo comando
        """
    await get_last_game_player_data(ctx, target_player= target_player, target_team= target_team)
    response = f"!last_game no esta continuado y se eliminará en futuras versiones en favor de !lg, considera usar ya el nuevo comando"
    await ctx.send(response)

@bot.command(name='lg')
async def get_last_game_player_data(ctx,
                                    target_player: str = commands.parameter(default=None, description="nombre o agente del jugador cuyos datos quieres saber"), 
                                    target_team: str= commands.parameter(default=None, description="OPCIONAL. Equipo donde quieres buscar al agente en cuestion (ally/enemy). No necesario en caso de busqueda por nombre. Si no se especifica y el mismo agente se jugo en ambos equipos se da por defecto el jugador rival")):
    """
        Proporciona el elo y porcentaje de tiro a la cabeza de cualquier jugador de tu ultima partida
        
        Ejemplos: !lg IMissHer !lg Sova enemy !lg Jett"
        """
    author = ctx.message.author
    player = get_player_data(player=author)
    errorCode = errorCodeList.handleErrorCode(player)
    if(errorCode != None):
        response = errorCode
    else:
        lg_response = get_last_match_data(region= player['region'], name= player['name'], tag= player['tag'], target_player= target_player, target_team= target_team)
        errorCode = errorCodeList.handleErrorCode(lg_response)
        if(errorCode != None):
            response = errorCode
        else:
            response = lg_response
    await ctx.send(response)

@bot.command(name='wr')
async def get_wr(ctx,target = commands.parameter(default=None, description="nombre del mapa o agente cuyo porcentaje de victorias quieres saber")):
    """
        Indica tu porcentaje de victoria con un agente o en un mapa concreto

        Ejemplos: !wr Omen !wr Split
        """
    #No target selected
    if(target == None):
        response = errorCodeList.handleErrorCode(errorCodeList.ERR_CODE_122)
    else:
        #Process the request
        author = ctx.message.author
        player = get_player_data(player=author)
        errorCode = errorCodeList.handleErrorCode(player)
        if(errorCode != None):
            response = errorCode
        else:
            wr = get_target_wr(region= player['region'], name= player['name'], tag= player['tag'], target= target)
            errorCode = errorCodeList.handleErrorCode(wr)
            if(errorCode != None):
                response = errorCode
            else:
                response = f"Tu win ratio con {target} es {wr}%"
    
    await ctx.send(response)

@bot.command(name='avg_elo')
async def get_average_elo(ctx):
    "Indica el elo medio de cada equipo de tu ultima partida"

    author = ctx.message.author
    player = get_player_data(player=author)
    errorCode = errorCodeList.handleErrorCode(player)
    if(errorCode != None):
        response = errorCode
    else:
        avg_elo = get_avg_elo(region= player['region'], name= player['name'], tag= player['tag'])
        errorCode = errorCodeList.handleErrorCode(avg_elo)
        if(errorCode != None):
            response = errorCode
        else:
            response = avg_elo
    
    await ctx.send(response)

@bot.command(name='peak')
async def peak(ctx,
                    target_player: str = commands.parameter(default=None, description="nombre o agente del jugador cuyo maximo elo quieres saber"), 
                    target_team: str= commands.parameter(default=None, description="OPCIONAL. Equipo donde quieres buscar al agente en cuestion (ally/enemy). No necesario en caso de busqueda por nombre. Si no se especifica y el mismo agente se jugo en ambos equipos se da por defecto el jugador rival")):
    """
        Proporciona el elo maximo que ha alcanzado cualquier jugador de tu ultima partida
        
        Ejemplos: !peak IMissHer !peak Sova enemy !peak Jett"
        """
    author = ctx.message.author
    player = get_player_data(player=author)
    errorCode = errorCodeList.handleErrorCode(player)
    if(errorCode != None):
        response = errorCode
    #Check first given command
    peakElo = peak_elo(region= player['region'], name= player['name'], tag= player['tag'], target_player= target_player, targetTeam= target_team)
    errorCode = errorCodeList.handleErrorCode(peakElo)
    if(errorCode != None):
        response = errorCode
    else:
        response = peakElo
    await ctx.send(response)

#To Do: borrar esta funcion cuando ya nadie la use
@bot.command(name='Mariano')
async def get_mariano_percentage_deprecate(ctx):
    """
        Porcentaje de victorias del gran Mariano
        !Mariano no esta continuado y se eliminará en futuras versiones en favor de !mariano, considera usar ya el nuevo comando
        """
    await get_mariano_percentage(ctx)
    response = f"!Mariano no esta continuado y se eliminará en futuras versiones en favor de !mariano, considera usar ya el nuevo comando"
    await ctx.send(response)

@bot.command(name='mariano')
async def get_mariano_percentage(ctx):
    "Porcentaje de victorias del gran Mariano"
    mariano_win_percentage = get_mariano_lost_percentage()
    errorCode = errorCodeList.handleErrorCode(mariano_win_percentage)
    if(errorCode != None):
        response = errorCode
    else:
        response = f"Mariano ha perdido el {mariano_win_percentage}% de las partidas que ha jugado. Que barbaridad"
    await ctx.send(response)

@bot.command(name='version')
async def get_version(ctx):
    "Version de PiumPiumBot que se esta ejecutando"
    response = f"{config.version}-{config.type[0]}"
    await ctx.send(response)



def main():
    token = get_bot_token()
    bot.run(token)

if __name__ == "__main__":
    main()