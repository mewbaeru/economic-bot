from disnake.ext import commands

from database.requests import get_daily_award, give_money, update_dayly_award, get_time_left
from modules import *

from datetime import datetime, timedelta
from random import randint

guild_id = Utils.get_guild_id()

class Timely(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.utils = Utils
    
    # daily award
    @commands.slash_command(name='timely', description='Временная награда', guild_ids=[guild_id])
    async def timely(self, ctx):
        logger.debug('/timely - start')

        need = datetime.fromtimestamp(int(await get_daily_award(ctx.author.id)))
        time = datetime.now()

        money = randint(50, 200)

        if len(str(need)) < 2 or time >= need:
            # add new transaction
            await add_transaction(self.ctx.author.id, f'Ежедневное вознаграждение', +money, datetime.now())

            await give_money(ctx.author.id, money)
            await update_dayly_award(ctx.author.id, int(datetime.timestamp(time + timedelta(hours=24))))

            embed = set_timely_embed(ctx, money)
            await ctx.response.send_message(embed=embed)
        else:
            time_left = await get_time_left(ctx.author.id)
            embed = set_time_left_embed(ctx, time_left)
            await ctx.response.send_message(embed=embed)

def setup(client):
    client.add_cog(Timely(client))