from disnake.ext import commands

from database.requests import get_shop_roles
from modules import *

import math

guild_id = Utils.get_guild_id()

# get cost additional role
try: 
    settings_roles, settings_prices = Utils.get_personal_roles()
except Exception:
    logger.error('failed to load settings')

class Shop(commands.Cog):
    def __init__(self, client):
        self.client = client
    
    @commands.slash_command(name='shop', description='Магазин личных ролей', guild_ids=[guild_id])
    async def shop(self, ctx):
        logger.debug('/shop - start')
        roles = await get_shop_roles()
        total_pages = math.ceil(len(roles)/5)
        page = 1
        
        if roles:
            embed = set_shop(ctx, roles, page, total_pages)
            await ctx.response.send_message(embed=embed, view=ShopView(ctx, page, roles, total_pages, settings_roles, settings_prices))
        else: 
            embed = set_empty_shop(ctx)
            await ctx.response.send_message(embed=embed)

def setup(client):
    client.add_cog(Shop(client))