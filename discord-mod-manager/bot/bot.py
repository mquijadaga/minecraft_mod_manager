from discord.ext import commands
import discord
from config import DISCORD_TOKEN
from db import init_db

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="/", intents=intents)


@bot.event
async def on_ready():
    await init_db()
    print(f"Bot conectado como {bot.user} (ID: {bot.user.id})")
    await bot.load_extension("cogs.settings")
    await bot.load_extension("cogs.mods")

def main():
    bot.run(DISCORD_TOKEN)

if __name__ == "__main__":
    main()