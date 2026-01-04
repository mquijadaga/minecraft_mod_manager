import discord
import requests
import os
from dotenv import load_dotenv
from discord.ext import commands

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
MODRITHM_TOKEN = os.getenv("MODRITHM_TOKEN")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="/", intents=intents)

settings = {}

def get_guild_settings(guild_id: int):
    """Devuelve el dict de ajustes para un servidor, creándolo si no existe."""
    if guild_id not in settings:
        settings[guild_id] = {
            "version": None,
            "loader": None,
            "mods": []
        }
    return settings[guild_id]

@bot.event
async def on_ready():
    print(f"Bot conectado como {bot.user} (ID: {bot.user.id})")

@bot.command()
async def setversion(ctx, version: str):
    cfg = get_guild_settings(ctx.guild.id)
    cfg["version"] = version
    await ctx.send(f"Versión del servidor establecida a **{version}**.")

@bot.command()
async def setloader(ctx, loader: str):
    loader = loader.lower()
    if loader not in ("forge", "neoforge", "fabric", "quilt"):
        await ctx.send("Loader no reconocido. Usa forge / neoforge / fabric / quilt.")
        return
    cfg = get_guild_settings(ctx.guild.id)
    cfg["loader"] = loader
    await ctx.send(f"Mod loader establecido a **{loader}**.")

@bot.command()
async def showconfig(ctx):
    cfg = get_guild_settings(ctx.guild.id)
    await ctx.send(
        f"Configuración actual del servidor:\n"
        f"Versión: `{cfg['version']}`\n"
        f"Loader: `{cfg['loader']}`\n"
        f"Mods: {len(cfg['mods'])} añadidos."
    )

bot.run(TOKEN)
