from discord.ext import commands
from valorantFDS import get_vct
from PiumPiumBot_Config import PiumPiumBot_Log

log = PiumPiumBot_Log()

class Esports(commands.Cog):
    "Commands related to Esports competitions"

    #To Do: investigar logos en el mensaje
    @commands.command(name='emea')
    async def get_emea(self, ctx):
        "Informacion de la VCT EMEA. Resultados de los partidos disputados y calendario proximo"
        log.startLog()
        response = get_vct("vct_emea")
        await ctx.send(response)
        log.finishLog(ctx.invoked_with)

    @commands.command(name='na')
    async def get_na(self, ctx):
        "Informacion de la VCT Americas. Resultados de los partidos disputados y calendario proximo"
        log.startLog()
        response = get_vct("vct_americas")
        await ctx.send(response)
        log.finishLog(ctx.invoked_with)

    @commands.command(name='koi')
    async def get_koi(self, ctx):
        "Informacion de KOI. Resultados de los partidos disputados y calendario proximo"
        log.startLog()
        response = get_vct("vct_emea", "KOI")
        await ctx.send(response)
        log.finishLog(ctx.invoked_with)

    @commands.command(name='th')
    async def get_th(self, ctx):
        "Informacion de Heretics. Resultados de los partidos disputados y calendario proximo"
        log.startLog()
        response = get_vct("vct_emea", "TH")
        await ctx.send(response)
        log.finishLog(ctx.invoked_with)

    @commands.command(name='gx')
    async def get_gx(self, ctx):
        "Informacion de GiantX. Resultados de los partidos disputados y calendario proximo"
        log.startLog()
        response = get_vct("vct_emea", "GX")
        await ctx.send(response)
        log.finishLog(ctx.invoked_with)

    @commands.command(name='nrg')
    async def get_nrg(self, ctx):
        "Informacion de NRG. Resultados de los partidos disputados y calendario proximo"
        log.startLog()
        response = get_vct("vct_americas", "NRG")
        await ctx.send(response)
        log.finishLog(ctx.invoked_with)

    @commands.command(name='sen')
    async def get_sen(self, ctx):
        "Informacion de Sentinels. Resultados de los partidos disputados y calendario proximo"
        log.startLog()
        response = get_vct("vct_americas", "SEN")
        await ctx.send(response)
        log.finishLog(ctx.invoked_with)