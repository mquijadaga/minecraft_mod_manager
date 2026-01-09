from discord.ext import commands
import discord
from bot.config import DISCORD_TOKEN
from bot.db import init_db

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="/", intents=intents)


@bot.event
async def on_ready():
    await init_db()
    print(f"Bot conectado como {bot.user} (ID: {bot.user.id})")
    await bot.load_extension("bot.cogs.settings")
    await bot.load_extension("bot.cogs.mods")

def main():
    bot.run(DISCORD_TOKEN)

if __name__ == "__main__":
    main()