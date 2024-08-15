from disnake.ext import commands

from database.requests import get_balance, transfer_money, add_transaction
from modules import *

guild_id = Utils.get_guild_id()

class Give(commands.Cog):
    def __init__(self, client):
        self.client = client
    
    # transer money
    @commands.slash_command(name="give", description="Передать валюту", guild_ids=[guild_id])
    async def give(ctx, member: disnake.Member = commands.Param(description='Введите пользователя, которому хотите перевести валюту'), 
                   amount: int = commands.Param(description='Введите сумму перевода')):
        logger.debug('/give - start')
        
        balance = await get_balance(ctx.author.id)
        
        if member.id == ctx.author.id:
            embed = set_invalid_user(ctx, 'Перевод валюты', 'себя')
            await ctx.response.send_message(embed=embed, ephemeral=True)
            return
        elif member.bot:
            embed = set_invalid_user(ctx, 'Перевод валюты', 'бота')
            await ctx.response.send_message(embed=embed, ephemeral=True)
            return
        
        if balance >= amount and amount > 0:
            await transfer_money(ctx.author.id, member.id, amount)

            logger.info(f"/give - sender: {ctx.author.id} - recipient: {member.id} - amount: {amount}")
            # add new transaction
            await add_transaction(ctx.author.id, f'Перевод валюты пользователю {member.mention}', -amount, datetime.now())
            await add_transaction(member.id, f'Перевод валюты от пользователя {ctx.author.mention}', +amount, datetime.now())

            embed = set_give_money(ctx, member, amount)
            await ctx.response.send_message(embed=embed)
        else:
            embed = set_invalid_money(ctx, 'Перевод валюты', await get_balance(ctx.author.id))
            await ctx.response.send_message(embed=embed, ephemeral=True)

def setup(client):
    client.add_cog(Give(client))