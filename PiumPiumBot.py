import discord
from discord.ext import commands
from PiumPiumBot_ErrorCodes import ErrorCodes
from PiumPiumBot_Config import PiumPiumBot_Config
from PiumPiumBot_Esports import Esports
from PiumPiumBot_InternalCommands import InternalCommands
from PiumPiumBot_GameCommands import GameCommands

intents = discord.Intents.all()
helper = commands.DefaultHelpCommand(width= 500, no_category = 'Comandos genericos')
bot = commands.Bot(command_prefix='!',intents=intents, help_command= helper)
errorCodeList = ErrorCodes()
config = PiumPiumBot_Config()

def get_bot_token():
    """
    Get Discord bot token to be used in any request. It must be stored in PiumPiumToken.txt

    Parameters:
        void

    Returns:
        Response: Bot token.
    """
    path = config.PRIVATE_PATH + "/PiumPiumToken.txt"
    tokenFile = open(path,"r")
    token = tokenFile.read()
    return token

@bot.event
async def on_ready():
    await bot.add_cog(Esports())
    await bot.add_cog(InternalCommands())
    await bot.add_cog(GameCommands())

def main():
    token = get_bot_token()
    bot.run(token)

if __name__ == "__main__":
    main()