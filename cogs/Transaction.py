from disnake.ext import commands

from database.requests import get_user_transactions, is_exists_transaction
from modules import *

import math

guild_id = Utils.get_guild_id()

class Transaction(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.utils = Utils()
    
    # balance
    @commands.slash_command(name='balance', description='Посмотреть баланс', guild_ids=[guild_id])
    async def balance(ctx, user: disnake.Member = commands.Param(default=None, description='Выберите пользователя для взаимодействия')):
        logger.debug('/balance - start')
        if user is None:
            user = ctx.author
        elif user.bot:
            embed = set_invalid_user(ctx, 'Текущий баланс', 'бота')
            await ctx.response.send_message(embed=embed, ephemeral=True)
            return

        embed = set_balance_user(ctx, user, await get_balance(user.id))
        await ctx.response.send_message(embed=embed)

    # transaction
    @commands.slash_command(name='transaction', description='Посмотреть транзакции', guild_ids=[guild_id])
    async def transaction(ctx, user: disnake.Member = commands.Param(default=None, description='Выберите пользователя для взаимодействия')):
        logger.debug('/transaction - start')
        if user is None:
            user = ctx.author
        elif user.bot:
            embed = set_invalid_user(ctx, 'Транзакции', 'бота')
            await ctx.response.send_message(embed=embed, ephemeral=True)
            return
        
        transactions = await get_user_transactions(user.id)
        total_pages = math.ceil(len(transactions)/10)
        page = 1

        if await is_exists_transaction(user.id):
            embed = set_transaction(ctx, user, transactions, page, total_pages)
            await ctx.response.send_message(embed=embed, view=TransactionView(ctx, user, page, transactions, total_pages))
        else:
            embed = set_not_transaction(ctx)
            await ctx.response.send_message(embed=embed, ephemeral=True)

def setup(client):
    client.add_cog(Transaction(client))