from disnake.ext import commands

from database.requests import get_balance, get_marry
from modules import *

guild_id = Utils.get_guild_id()

# get role data from settings
try: 
    settings_roles, settings_prices = Utils.get_personal_roles()
except Exception:
    logger.error('failed to load settings')

class Marry(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.utils = Utils
    
    @commands.slash_command(name='marry', description='Заключить брак', guild_ids=[guild_id])
    async def marry(self, ctx, member: disnake.Member = commands.Param(description='Введите пользователя, с которым хотите заключить брак')):
        logger.debug('/marry - start')

        cost_marry = settings_prices.get('marry_create')
        role_marry = settings_roles.get('marry_role')
        balance = await get_balance(ctx.author.id)

        if member.id == ctx.author.id:
            embed = set_invalid_user(ctx, 'Заключить брак', 'себя')
            await ctx.response.send_message(embed=embed, ephemeral=True)
            return
        elif member.bot:
            embed = set_invalid_user(ctx, 'Заключить брак', 'бота')
            await ctx.response.send_message(embed=embed, ephemeral=True)
            return
        
        if await get_marry(ctx.author.id):
            embed = set_active_marry(ctx)
            await ctx.response.send_message(embed=embed, ephemeral=True)
            return
        elif await get_marry(member.id):
            embed = set_active_marry_member(ctx, member)
            await ctx.response.send_message(embed=embed, ephemeral=True)
            return

        if balance >= cost_marry:
            embed = set_marry(ctx, member)
            await ctx.response.send_message(embed=embed, view=MarryView(ctx, member, role_marry, cost_marry))
        else: 
            embed = set_invalid_money(ctx, 'Заключить брак', await get_balance(ctx.author.id))
            await ctx.response.send_message(embed=embed, ephemeral=True)
        
def setup(client):
    client.add_cog(Marry(client))