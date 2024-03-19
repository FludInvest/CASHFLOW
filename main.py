from threading import Thread

from discord_classes import *
from disnake.ext import commands
from disnake import TextInputStyle, ModalInteraction
from discord_webhook import DiscordWebhook, DiscordEmbed
import disnake

from config import *
from base import *

from logic.get_data import *


bot = commands.Bot()

@bot.event
async def on_ready():
    pass
if __name__ == "__main__":
    asyncio.run(get_threads())
    bot.run(tokens['discord'])


