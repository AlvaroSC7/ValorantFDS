import discord
from discord.ext import commands
from os.path import dirname, abspath
from valorantFDS import get_last_match_HS_percentage, get_player_data, get_mariano_lost_percentage, get_this_season_elo, get_last_match_player_data, get_target_wr, _get_target_type, get_last_match_agent_data
from PiumPiumBot_ErrorCodes import ErrorCodes, handleErrorCode

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
bot = commands.Bot(command_prefix='!',intents=intents)
errorCodeList = ErrorCodes()

##################################################################
#                         COMMANDS                               #
##################################################################
#To Do: comando sens
#To Do: comando peak elo
#To Do: comando average_elo de un lobby
#To Do: comando para setear datos de jugadores
#To Do: comando para obtener mira
#To Do: comando sonido ace
#To Do: comando acs last game
#To Do: comando help. Add it to "Sobre mi" en el bot en Discord Developer.
#To Do: comando que implemente bug ticket. Envia un correo a mi email, que se saca de un txt privado
#To Do: Implement !esports !vct !masters

#To Do: borrar esta funcion cuando ya nadie la use
@bot.command(name='HS')
async def get_HS_percentage_deprecate(ctx):
    await get_HS_percentage(ctx)
    response = f"!HS no esta continuado y se eliminará en futuras versiones en favor de !hs, considera usar ya el nuevo comando"
    await ctx.send(response)

@bot.command(name='hs')
async def get_HS_percentage(ctx):
    author = ctx.message.author
    player = get_player_data(player=author)
    errorCode = handleErrorCode(player)
    if(errorCode != None):
        await ctx.send(errorCode)
    else:
        HS_accuracy = get_last_match_HS_percentage(region= player['region'], name= player['name'], tag= player['tag'])
        errorCode = handleErrorCode(HS_accuracy)
        if(errorCode != None):
            await ctx.send(errorCode)
        else:
            response = f"Tu precision en la ultima partida fue: {HS_accuracy}%"
            await ctx.send(response)

@bot.command(name='elo')
async def get_elo(ctx):
    author = ctx.message.author
    player = get_player_data(player=author)
    errorCode = handleErrorCode(player)
    if(errorCode != None):
        await ctx.send(errorCode)
    else:
        elo = get_this_season_elo(region= player['region'], name= player['name'], tag= player['tag'])
        errorCode = handleErrorCode(elo)
        if(errorCode != None):
            await ctx.send(errorCode)
        else:
            await ctx.send("No se han encontrado partidas recientes ni datos de usuario")

@bot.command(name='last_game')
async def get_last_game_player_data(ctx,target_player: str= None,target_team: str= None):
    author = ctx.message.author
    player = get_player_data(player=author)
    errorCode = handleErrorCode(player)
    if(errorCode != None):
        await ctx.send(errorCode)
    #Check first given command
    if(target_player == None):
        print(f"{errorCodeList.ERR_CODE_122}")
        await ctx.send(handleErrorCode(errorCodeList.ERR_CODE_122))
    elif(target_team != None and target_team.lower() != "enemy" and target_team.lower() != "ally"):
        print(f"{errorCodeList.ERR_CODE_123}")
        await ctx.send(handleErrorCode(errorCodeList.ERR_CODE_123))
    else:
        #Check if target is player name or player character
        target_type = _get_target_type(target= target_player)
        errorCode = handleErrorCode(target_type)
        if(errorCode != None):
            await ctx.send(errorCode)
        if(target_type == "map"):
            await ctx.send("Has seleccionado un mapa. Selecciona un nombre de jugador o de agente para revisar sus datos. Ejemplo: !last_game shadowdanna | !last_game Reyna")
        else:
            #Target type (only type is assured) is valid
            if(target_type == "agent"):
                #Get elo and HS of the player controlling the selected agent in last player's game
                targetData = get_last_match_agent_data(region= player['region'], name= player['name'], tag= player['tag'], targetAgent= target_player, targetTeam= target_team)
                errorCode = handleErrorCode(targetData)
                if(errorCode != None):
                    await ctx.send(errorCode)
                else:
                    response = f"{targetData['name']}" + f"\n\t{targetData['elo']}" + f"\n\tPorcentaje de headshot: {targetData['HS']}%"
            else:
                #Get elo and HS of the selected player
                targetData = get_last_match_player_data(region= player['region'], name= player['name'], tag= player['tag'], targetName= target_player)
                errorCode = handleErrorCode(targetData)
                if(errorCode != None):
                    await ctx.send(errorCode)
                else:
                    response = f"{target_player}" + f"\n\t{targetData['elo']}" + f"\n\tPorcentaje de headshot: {targetData['HS']}%"
            await ctx.send(response)

@bot.command(name='wr')
async def get_wr(ctx,target=None):
    #No target selected
    if(target == None):
        await ctx.send("Selecciona un mapa o agente para consultar tu win ratio. Ejemplo: !wr Haven | !wr Yoru")
    else:
        #Process the request
        author = ctx.message.author
        player = get_player_data(player=author)
        errorCode = handleErrorCode(player)
        if(errorCode != None):
            await ctx.send(errorCode)
        else:
            wr = get_target_wr(region= player['region'], name= player['name'], tag= player['tag'], target= target)
            errorCode = handleErrorCode(wr)
            if(errorCode != None):
                await ctx.send(errorCode)
            else:
                await ctx.send(f"Tu win ratio con {target} es {wr}%")

@bot.command(name='Mariano')
async def get_mariano_percentage(ctx):
    mariano_win_percentage = get_mariano_lost_percentage()
    errorCode = handleErrorCode(mariano_win_percentage)
    if(errorCode != None):
        await ctx.send(errorCode)
    else:
        response = f"Mariano ha perdido el {mariano_win_percentage}% de las partidas que ha jugado. Que barbaridad"
        await ctx.send(response)



def main():
    token = get_bot_token()
    bot.run(token)

if __name__ == "__main__":
    main()