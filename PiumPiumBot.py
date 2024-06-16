import discord
from discord.ext import commands
from os.path import dirname, abspath
from valorantFDS import get_last_match_HS_percentage, get_player_data, get_mariano_lost_percentage

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

@bot.command(name='suma')
async def sumar(ctx, num1, num2):
    response = int(num1) + int(num2)
    await ctx.send(response)

@bot.command(name='HS')
async def get_HS_percentage(ctx):
    author = ctx.message.author
    player = get_player_data(player=author)
    HS_accuracy = get_last_match_HS_percentage(region= player['region'], name= player['name'], tag= player['tag'])
    response = f"Your accuracy in the last game was: {HS_accuracy}%"
    await ctx.send(response)

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