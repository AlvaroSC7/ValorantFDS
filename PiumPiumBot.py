import discord
from discord.ext import commands
from os.path import dirname, abspath
from valorantFDS import get_last_match_HS_percentage, get_player_data, get_mariano_lost_percentage, get_this_season_elo, get_last_match_player_data

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

@bot.command(name='wr')
async def get_wr(ctx,target):
    author = ctx.message.author
    player = get_player_data(player=author)
    elo = get_this_season_elo(region= player['region'], name= player['name'], tag= player['tag'])
    await ctx.send(elo)

@bot.command(name='Mariano')
async def get_mariano_percentage(ctx):
    mariano_win_percentage = get_mariano_lost_percentage()
    response = f"Mariano ha perdido el {mariano_win_percentage}% de las partidas que ha jugado. Que barbaridad"
    await ctx.send(response)

def main():
    token = get_bot_token()
    bot.run(token)

if __name__ == "__main__":
    main()