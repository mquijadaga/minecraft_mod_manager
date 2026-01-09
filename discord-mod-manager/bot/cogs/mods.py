import discord
from discord.ext import commands
import requests
import json
from db import get_guild_settings

BASE_API_URL = "https://api.modrinth.com/v2"

class ModListView(discord.ui.View):
    def __init__(self, mods: list[dict]):
        super().__init__()
        self.mods = mods

        for index, mod in enumerate(mods[:5], start=1):
            self.add_item(ModButton(label=f"{index}. {mod['name']}", mod_id=mod['mod_id']))


class ModButton(discord.ui.Button):
    def __init__(self, label: str, mod_id: str):
        super().__init__(label=label, style=discord.ButtonStyle.primary)
        self.mod_id = mod_id

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_message(f"Haz hecho clic en el mod: {self.label} ({self.mod_id})", ephemeral=True)

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
        mods_for_view = []
        for i, hit in enumerate(data["hits"][:2], start=1):
            mod_id = hit["project_id"]
            name = hit["title"]
            slug = hit["slug"]
            url = f"https://modrinth.com/mod/{slug}"
            lines.append(f"**{i}.** [{name}]({url})")
            mods_for_view.append({"name": name, "mod_id": mod_id})
            print(name, get_mod_dependencies(mod_id, cfg['version'], cfg['loader']))

        description = "\n".join(lines)
        embed = discord.Embed(
            title=f"Resultados para: {query}",
            description=description,
            color=discord.Color.blue(),
        )

        view = ModListView(mods_for_view)
        await ctx.send(embed=embed, view=view)

def get_mod_dependencies(mod_id:str, version: str, loader: str):
    headers = {
        "User-Agent": "DiscordMinecraftModManager/1.0 (contact: mquijadaga)",
    }
    try:
        r = requests.get(
            f"{BASE_API_URL}/project/{mod_id}/dependencies",
            headers=headers,
            timeout=10,
        )
    except requests.exceptions.ReadTimeout:
        print("Modrinth request timed out")
        return []
    except requests.exceptions.RequestException as e:
        print("Error al llamar a Modrinth:", e)
        return []
    
    if r.status_code != 200:
        print("Error al conectar con la API de Modrinth.")
        return []

    data = r.json()
    dependencies = []

    for project in data.get("projects", []):
        print("Found project:", project.get("slug"))
    for ver in data.get("versions", []):
        if version not in ver.get("version_number", ""):
            continue
        if loader not in ver.get("loaders", []):
            continue

        for dep in ver.get("dependencies", []):
            if dep.get("dependency_type") == "required":
                dependencies.append({
                    "project": dep,
                    "version_id": dep.get("version_id"),
                })
    return dependencies

async def setup(bot):
    await bot.add_cog(Mods(bot))