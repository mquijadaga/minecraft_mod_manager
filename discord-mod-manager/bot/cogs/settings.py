from discord.ext import commands
from db import get_guild_settings, set_guild_settings

class Settings(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='setconfig', help='Establece la configuración del servidor para la búsqueda de mods. Uso: /setconfig <version> <loader>')
    async def setconfig(self, ctx, version: str, loader: str):
        await set_guild_settings(ctx.guild.id, version, loader)
        await ctx.send(f"Configuración actualizada: Versión = {version}, Cargador = {loader}")
    
    @commands.command(name='getconfig', help='Obtiene la configuración actual del servidor para la búsqueda de mods.')
    async def getconfig(self, ctx):
        cfg = await get_guild_settings(ctx.guild.id)
        if cfg:
            await ctx.send(f"Configuración actual: Versión = {cfg['version']}, Cargador = {cfg['loader']}")
        else:
            await ctx.send("No hay configuración establecida para este servidor.")

async def setup(bot):
    await bot.add_cog(Settings(bot))