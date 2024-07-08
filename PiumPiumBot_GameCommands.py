from discord.ext import commands
import discord
import logging
from os.path import isfile
from PiumPiumBot_Config import PiumPiumBot_Config, PiumPiumBot_Log
from valorantFDS import RoulettePool
import valorantFDS as valorant
from PiumPiumBot_ErrorCodes import ErrorCodes

errorCodeList = ErrorCodes()
logger = logging.getLogger(__name__)
config = PiumPiumBot_Config()
log = PiumPiumBot_Log()
roulette = RoulettePool()

##################################################################
#                         COMMANDS                               #
##################################################################
#To Do: comando sens
#To Do: comando para obtener mira
#To Do: comando sonido ace
#To Do: comando acs last game
#To Do: comando que implemente bug ticket. Envia un correo a mi email, que se saca de un txt privado
#To Do: Implement !champions when format is known

class GameCommands(commands.Cog):
    "Comandos relacionados con datos del juego y partidas del jugador"

    @commands.command(name='hs')
    async def get_HS_percentage(self, ctx):
        "Porcentaje de headshot de tu ultima partida"
        log.startLog()
        author = ctx.message.author
        player = valorant.get_player_data(player=author)
        errorCode = errorCodeList.handleErrorCode(player)
        if(errorCode != None):
            response = errorCode
        else:
            HS_accuracy = valorant.get_last_match_HS_percentage(region= player['region'], name= player['name'], tag= player['tag'])
            errorCode = errorCodeList.handleErrorCode(HS_accuracy)
            if(errorCode != None):
                response = errorCode
            elif(HS_accuracy == None):
                response = "RIOT no proporciona datos de precision en los Deathmatch"
            else:
                response = f"Tu precision en la ultima partida fue: {HS_accuracy}%"
        await ctx.send(response)
        log.finishLog(ctx.invoked_with)

    @commands.command(name='elo')
    async def get_elo(self, ctx):
        "Tu elo actual"
        log.startLog()
        author = ctx.message.author
        player = valorant.get_player_data(player=author)
        errorCode = errorCodeList.handleErrorCode(player)
        if(errorCode != None):
            response = errorCode
        else:
            elo = valorant.get_this_season_elo(region= player['region'], name= player['name'], tag= player['tag'])
            errorCode = errorCodeList.handleErrorCode(elo)
            if(errorCode != None):
                response = errorCode
            else:
                response = elo

        await ctx.send(response)
        log.finishLog(ctx.invoked_with)

    @commands.command(name='lg')
    async def get_last_game_player_data(self, ctx,
                                        target_player: str = commands.parameter(default=None, description="nombre o agente del jugador cuyos datos quieres saber"), 
                                        target_team: str= commands.parameter(default=None, description="OPCIONAL. Equipo donde quieres buscar al agente en cuestion (ally/enemy). No necesario en caso de busqueda por nombre. Si no se especifica y el mismo agente se jugo en ambos equipos se da por defecto el jugador rival")):
        "Informacion de un jugador de tu ultima partida. Ejemplos: !lg IMissHer !lg Sova enemy !lg Jett"
        log.startLog()
        author = ctx.message.author
        player = valorant.get_player_data(player=author)
        errorCode = errorCodeList.handleErrorCode(player)
        if(errorCode != None):
            response = errorCode
        else:
            lg_response = valorant.get_last_match_data(region= player['region'], name= player['name'], tag= player['tag'], target_player= target_player, target_team= target_team)
            errorCode = errorCodeList.handleErrorCode(lg_response)
            if(errorCode != None):
                response = errorCode
            else:
                response = lg_response
        await ctx.send(response)
        log.finishLog(ctx.invoked_with)

    @commands.command(name='wr')
    async def get_wr(self, ctx,target = commands.parameter(default=None, description="nombre del mapa o agente cuyo porcentaje de victorias quieres saber")):
        "Tu porcentaje de victoria con un agente o en un mapa"
        log.startLog()
        #No target selected
        if(target == None):
            response = errorCodeList.handleErrorCode(errorCodeList.ERR_CODE_122)
        else:
            #Process the request
            author = ctx.message.author
            player = valorant.get_player_data(player=author)
            errorCode = errorCodeList.handleErrorCode(player)
            if(errorCode != None):
                response = errorCode
            else:
                wr = valorant.get_target_wr(region= player['region'], name= player['name'], tag= player['tag'], target= target)
                errorCode = errorCodeList.handleErrorCode(wr)
                if(errorCode != None):
                    response = errorCode
                else:
                    response = f"Tu win ratio con {target} es {wr}%"

        await ctx.send(response)
        log.finishLog(ctx.invoked_with)

    @commands.command(name='avg_elo')
    async def get_average_elo(self, ctx):
        "Elo medio de cada equipo de tu ultima partida"
        log.startLog()
        author = ctx.message.author
        player = valorant.get_player_data(player=author)
        errorCode = errorCodeList.handleErrorCode(player)
        if(errorCode != None):
            response = errorCode
        else:
            avg_elo = valorant.get_avg_elo(region= player['region'], name= player['name'], tag= player['tag'])
            errorCode = errorCodeList.handleErrorCode(avg_elo)
            if(errorCode != None):
                response = errorCode
            else:
                response = avg_elo

        await ctx.send(response)
        log.finishLog(ctx.invoked_with)

    @commands.command(name='peak')
    async def peak(self, ctx,
                        target_player: str = commands.parameter(default=None, description="nombre o agente del jugador cuyo maximo elo quieres saber"), 
                        target_team: str= commands.parameter(default=None, description="OPCIONAL. Equipo donde quieres buscar al agente en cuestion (ally/enemy). No necesario en caso de busqueda por nombre. Si no se especifica y el mismo agente se jugo en ambos equipos se da por defecto el jugador rival")):
        "Elo maximo que ha alcanzado cualquier jugador de tu ultima partida. Ejemplos: !peak IMissHer !peak Sova enemy !peak Jett"
        log.startLog()
        author = ctx.message.author
        player = valorant.get_player_data(player=author)
        errorCode = errorCodeList.handleErrorCode(player)
        if(errorCode != None):
            response = errorCode
        #Check first given command
        peakElo = valorant.peak_elo(region= player['region'], name= player['name'], tag= player['tag'], target_player= target_player, targetTeam= target_team)
        errorCode = errorCodeList.handleErrorCode(peakElo)
        if(errorCode != None):
            response = errorCode
        else:
            response = peakElo
        await ctx.send(response)
        log.finishLog(ctx.invoked_with)

    @commands.command(name='mariano')
    async def get_mariano_percentage(self, ctx):
        "Porcentaje de victorias del gran Mariano"
        log.startLog()
        mariano_win_percentage = valorant.get_mariano_lost_percentage()
        errorCode = errorCodeList.handleErrorCode(mariano_win_percentage)
        if(errorCode != None):
            response = errorCode
        else:
            response = f"Mariano ha perdido el {mariano_win_percentage}% de las partidas que ha jugado. Que barbaridad"
        await ctx.send(response)
        log.finishLog(ctx.invoked_with)

    @commands.command(name='ruleta')
    async def get_roulette(self, ctx, 
                        command: str= commands.parameter(default=None, description="OPCIONAL. Resetea que agentes te pueden tocar si escribes !ruleta reset")):
        "Te asigna un agente aleatorio"
        log.startLog()
        author = ctx.message.author
        player = valorant.get_player_data(player=author)
        errorCode = errorCodeList.handleErrorCode(player)
        if(errorCode != None):
            response = errorCode
        else:
            #Check first given command
            if(command == "reset"):
                roulette.resetPool()
                response = "Ruleta reseteada"
                agent = None
            elif(command == None):
                agent = roulette.getRandomAgent()
                if(errorCodeList.isErrorCode(agent)):
                    response = agent
                else:
                    response = f"{player['name']}:\n\t{agent}"
            else:
                response = errorCodeList.handleErrorCode(errorCodeList.ERR_CODE_125)

            await ctx.send(response)
            if(agent == "KAY/O"):   #Official name is not valid for a file
                agent = "KAYO"
            gifFile = config.ICON_PATH + f"/{agent}.gif"
            if(isfile(gifFile)):
                await ctx.send(file= discord.File(gifFile))
        log.finishLog(ctx.invoked_with)

    def bot_reset_roulette():
        "Function to be called periodically to reset automatically roulette pool"
        if(len(roulette.pool) < roulette.totalPoolSize):
            log.startLog()
            roulette.resetPool()
            log.finishLog("Automatically resetted roulette")