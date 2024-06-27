from discord.ext import commands
from PiumPiumBot_Config import PiumPiumBot_Config

config = PiumPiumBot_Config()

##################################################################
#                         COMMANDS                               #
##################################################################

class InternalCommands(commands.Cog):
    "Comandos para la configuracion del bot y obtencion de informacion del mismo"
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