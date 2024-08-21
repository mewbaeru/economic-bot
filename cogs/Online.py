from disnake.ext import commands

from database.requests import get_user_voice_activity_data
from modules import *

from datetime import datetime, timedelta

guild_id = Utils.get_guild_id()

class Online(commands.Cog):
    def __init__(self, client):
        self.client = client
    
    # voice activity
    @commands.slash_command(name='online', description='Голосовой онлайн', guild_ids=[guild_id])
    async def online(ctx, member: disnake.Member = commands.Param(default=None, description='Выберите пользователя')):
        logger.debug('/online - start')
        if member is None:
            member = ctx.author
        elif member.bot:
            embed = set_invalid_user(ctx, 'Голосовой онлайн', 'бота')
            await ctx.response.send_message(embed=embed, ephemeral=True)
            return
        
        online_data = await get_user_voice_activity_data(member.id)

        embed = set_online_user(ctx, member, online_data[2], online_data[3])
        await ctx.response.send_message(embed=embed)

def setup(client):
    client.add_cog(Online(client))