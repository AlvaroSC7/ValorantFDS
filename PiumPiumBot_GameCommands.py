from discord.ext import commands
import logging
from PiumPiumBot_Config import PiumPiumBot_Config, PiumPiumBot_Log
from valorantFDS import get_last_match_HS_percentage, get_player_data, get_mariano_lost_percentage, get_this_season_elo, get_target_wr, get_avg_elo, peak_elo, get_last_match_data
from PiumPiumBot_ErrorCodes import ErrorCodes

errorCodeList = ErrorCodes()
logger = logging.getLogger(__name__)
config = PiumPiumBot_Config()
log = PiumPiumBot_Log()

##################################################################
#                         COMMANDS                               #
##################################################################
#To Do: comando sens
#To Do: comando para obtener mira
#To Do: comando sonido ace
#To Do: comando acs last game
#To Do: comando que implemente bug ticket. Envia un correo a mi email, que se saca de un txt privado
#To Do: Implement !champions when format is known
#!peak y !lg KAYO no funciona de ninguna manera

class GameCommands(commands.Cog):
    "Comandos relacionados con datos del juego y partidas del jugador"
    #To Do: borrar esta funcion cuando ya nadie la use
    @commands.command(name='HS')
    async def get_HS_percentage_deprecate(self, ctx):
        """ 
            Indica el porcentaje de tiros a la cabeza que has tenido en tu ultima partida

            !HS no esta continuado y se eliminará en futuras versiones en favor de !hs, considera usar ya el nuevo comando
            """
        legacyLog = PiumPiumBot_Log()
        legacyLog.startLog()
        await self.get_HS_percentage(ctx)
        response = f"!HS no esta continuado y se eliminará en futuras versiones en favor de !hs, considera usar ya el nuevo comando"
        await ctx.send(response)
        legacyLog.finishLog(ctx.invoked_with)

    @commands.command(name='hs')
    async def get_HS_percentage(self, ctx):
        "Indica el porcentaje de tiros a la cabeza que has tenido en tu ultima partida"
        log.startLog()
        author = ctx.message.author
        player = get_player_data(player=author)
        errorCode = errorCodeList.handleErrorCode(player)
        if(errorCode != None):
            response = errorCode
        else:
            HS_accuracy = get_last_match_HS_percentage(region= player['region'], name= player['name'], tag= player['tag'])
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
        "Indica tu elo actual como {Rango} - {Puntuacion total en el sistema de rangos}"
        log.startLog()
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
        log.finishLog(ctx.invoked_with)

    #To Do: borrar esta funcion cuando ya nadie la use
    @commands.command(name='last_game')
    async def get_last_game_player_data_deprecate(self, ctx,
                                                  target_player: str = commands.parameter(default=None, description="nombre o agente del jugador cuyos datos quieres saber"), 
                                                  target_team: str= commands.parameter(default=None, description="OPCIONAL. Equipo donde quieres buscar al agente en cuestion (ally/enemy). No necesario en caso de busqueda por nombre. Si no se especifica y el mismo agente se jugo en ambos equipos se da por defecto el jugador rival")):
        """
            Proporciona el elo y porcentaje de tiro a la cabeza de cualquier jugador de tu ultima partida

            Ejemplos: !lg IMissHer !lg Sova enemy !lg Jett"

            !last_game no esta continuado y se eliminará en futuras versiones en favor de !lg, considera usar ya el nuevo comando
            """
        log.startLog()
        await self.get_last_game_player_data(ctx, target_player= target_player, target_team= target_team)
        response = f"!last_game no esta continuado y se eliminará en futuras versiones en favor de !lg, considera usar ya el nuevo comando"
        await ctx.send(response)
        log.finishLog(ctx.invoked_with)

    @commands.command(name='lg')
    async def get_last_game_player_data(self, ctx,
                                        target_player: str = commands.parameter(default=None, description="nombre o agente del jugador cuyos datos quieres saber"), 
                                        target_team: str= commands.parameter(default=None, description="OPCIONAL. Equipo donde quieres buscar al agente en cuestion (ally/enemy). No necesario en caso de busqueda por nombre. Si no se especifica y el mismo agente se jugo en ambos equipos se da por defecto el jugador rival")):
        """
            Proporciona el elo y porcentaje de tiro a la cabeza de cualquier jugador de tu ultima partida

            Ejemplos: !lg IMissHer !lg Sova enemy !lg Jett"
            """
        log.startLog()
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
        log.finishLog(ctx.invoked_with)

    @commands.command(name='wr')
    async def get_wr(self, ctx,target = commands.parameter(default=None, description="nombre del mapa o agente cuyo porcentaje de victorias quieres saber")):
        """
            Indica tu porcentaje de victoria con un agente o en un mapa concreto

            Ejemplos: !wr Omen !wr Split
            """
        log.startLog()
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
        log.finishLog(ctx.invoked_with)

    @commands.command(name='avg_elo')
    async def get_average_elo(self, ctx):
        "Indica el elo medio de cada equipo de tu ultima partida"
        log.startLog()
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
        log.finishLog(ctx.invoked_with)

    @commands.command(name='peak')
    async def peak(self, ctx,
                        target_player: str = commands.parameter(default=None, description="nombre o agente del jugador cuyo maximo elo quieres saber"), 
                        target_team: str= commands.parameter(default=None, description="OPCIONAL. Equipo donde quieres buscar al agente en cuestion (ally/enemy). No necesario en caso de busqueda por nombre. Si no se especifica y el mismo agente se jugo en ambos equipos se da por defecto el jugador rival")):
        """
            Proporciona el elo maximo que ha alcanzado cualquier jugador de tu ultima partida

            Ejemplos: !peak IMissHer !peak Sova enemy !peak Jett"
            """
        log.startLog()
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
        log.finishLog(ctx.invoked_with)

    #To Do: borrar esta funcion cuando ya nadie la use
    @commands.command(name='Mariano')
    async def get_mariano_percentage_deprecate(self, ctx):
        """
            Porcentaje de victorias del gran Mariano
            !Mariano no esta continuado y se eliminará en futuras versiones en favor de !mariano, considera usar ya el nuevo comando
            """
        legacyLog = PiumPiumBot_Log()
        legacyLog.startLog()
        await self.get_mariano_percentage(ctx)
        response = f"!Mariano no esta continuado y se eliminará en futuras versiones en favor de !mariano, considera usar ya el nuevo comando"
        await ctx.send(response)
        legacyLog.finishLog(ctx.invoked_with)

    @commands.command(name='mariano')
    async def get_mariano_percentage(self, ctx):
        "Porcentaje de victorias del gran Mariano"
        log.startLog()
        mariano_win_percentage = get_mariano_lost_percentage()
        errorCode = errorCodeList.handleErrorCode(mariano_win_percentage)
        if(errorCode != None):
            response = errorCode
        else:
            response = f"Mariano ha perdido el {mariano_win_percentage}% de las partidas que ha jugado. Que barbaridad"
        await ctx.send(response)
        log.finishLog(ctx.invoked_with)
