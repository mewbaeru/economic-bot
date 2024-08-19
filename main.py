import asyncio
import os
from dotenv import load_dotenv

import disnake
from disnake.ext import commands

from modules import *
from database.models import async_main

intetns = disnake.Intents.all()
client = commands.Bot(command_prefix='/', intents=intetns, case_insensitive=True)

async def connect_to_db():
    logger.info('Connecting to the db')
    await async_main()

# load cogs
for directory in ['./cogs', './cogs/voice_channels']:
    for filename in os.listdir(directory):
        if filename.endswith('.py'):
            if directory == './cogs':
                client.load_extension(f'cogs.{filename[:-3]}')
            elif directory == './cogs/voice_channels':
                client.load_extension(f'cogs.voice_channels.{filename[:-3]}')

asyncio.run(connect_to_db())

logger.info('Bot is ready')
load_dotenv()
client.run(os.getenv('TOKEN'))