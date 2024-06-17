import discord
from discord.ext import commands
from os.path import dirname, abspath
from valorantFDS import get_last_match_HS_percentage, get_player_data, get_mariano_lost_percentage, get_this_season_elo, get_last_match_player_data, get_target_wr

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

@bot.command(name='HS')
async def get_HS_percentage(ctx):
    author = ctx.message.author
    player = get_player_data(player=author)
    HS_accuracy = get_last_match_HS_percentage(region= player['region'], name= player['name'], tag= player['tag'])
    response = f"Your accuracy in the last game was: {HS_accuracy}%"
    await ctx.send(response)

@bot.command(name='elo')
async def get_elo(ctx):
    author = ctx.message.author
    player = get_player_data(player=author)
    elo = get_this_season_elo(region= player['region'], name= player['name'], tag= player['tag'])
    await ctx.send(elo)

#To Do: bugfix coger nombres con espacios
@bot.command(name='last_game')
async def get_last_game_player_data(ctx,target_player: str):
    author = ctx.message.author
    player = get_player_data(player=author)
    targetData = get_last_match_player_data(region= player['region'], name= player['name'], tag= player['tag'], targetName= target_player)
    if(targetData == None):
        response = "No se ha encontrado al jugador en la ultima partida"
    else:
        response = f"{target_player}" + f"\n\t{targetData['elo']}" + f"\n\tPorcentaje de headshot: {targetData['HS']}%"
    await ctx.send(response)

#To Do: comando sens
#To Do: comando peak elo
#To Do: comando average_elo de un lobby
#To Do: comando para setear datos de jugadores
#To Do: comando para obtener mira
#To Do: comando sonido ace
#To Do: comando acs last game

@bot.command(name='wr')
async def get_wr(ctx,target):
    #No target selected
    if(target == None):
        await ctx.send("Selecciona un mapa o agente para consultar tu win ratio. Ejemplo: !wr Haven | !wr Yoru")
    else:
        #Process the request
        author = ctx.message.author
        player = get_player_data(player=author)
        wr = get_target_wr(region= player['region'], name= player['name'], tag= player['tag'], target= target)
        #Check if map or agent do exist
        if(wr == None):
            await ctx.send("PiumPium no conoce ese mapa o agente :(")
        else:
            await ctx.send(f"Tu win ratio con {target} es {wr}%")

@bot.command(name='Mariano')
async def get_mariano_percentage(ctx):
    mariano_win_percentage = get_mariano_lost_percentage()
    response = f"Mariano ha perdido el {mariano_win_percentage}% de las partidas que ha jugado. Que barbaridad"
    await ctx.send(response)

#To Do: Implement !last_game Reyna enemy

#To Do: Implement !esports !vct !masters



def main():
    token = get_bot_token()
    bot.run(token)

if __name__ == "__main__":
    main()