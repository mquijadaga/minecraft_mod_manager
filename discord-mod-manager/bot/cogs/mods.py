from discord.ext import commands
import requests
import json
from db import get_guild_settings

BASE_API_URL = "https://api.modrinth.com/v2"

class Mods(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='search', help='Busca mods en Modrinth con filtros basados en la configuración del servidor.')
    async def modsearch(self, ctx, *, query: str):
        cfg = await get_guild_settings(ctx.guild.id)
        facets = [
            [f"project_type:mod"],
            [f"versions:{cfg['version']}"],
            [f"categories:{cfg['loader']}"]
        ]

        params = {
            "query": query,
            "limit": 5,
            "facets": json.dumps(facets)
        }

        headers = {
            "User-Agent": "DiscordMinecraftModManager/1.0 (contact: mquijadaga)",
        }
        print("Enviando solicitud a Modrinth con parámetros:", params)
        try:
            r = requests.get(
                f"{BASE_API_URL}/search",
                params=params,
                headers=headers,
                timeout=10,
            )
        except requests.exceptions.ReadTimeout:
            print("Modrinth request timed out")
            await ctx.send("La API de Modrinth tardó demasiado en responder (timeout).")
            return
        except requests.exceptions.RequestException as e:
            print("Error al llamar a Modrinth:", e)
            await ctx.send("Error de red al conectar con la API de Modrinth.")
            return
        
        if r.status_code != 200:
            await ctx.send("Error al conectar con la API de Modrinth.")
            return

        data = r.json()
        if not data["hits"]:
            await ctx.send("No se encontraron mods con esos filtros.")
            return

        lines = []
        for hit in data["hits"]:
            lines.append(f"**{hit['title']}** - {hit['slug']}")

        await ctx.send("\n".join(lines))

async def setup(bot):
    await bot.add_cog(Mods(bot))