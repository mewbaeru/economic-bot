import disnake 
from disnake.ext import commands

from database.requests import get_balance
from modules import *

guild_id = Utils.get_guild_id()

class Games(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.utils = Utils()

    # coinflip
    @commands.slash_command(name='coinflip', description='Подбросить монетку', guild_ids=[guild_id])
    async def coinflip(self, ctx, amount: int = commands.Param(description='Введите сумму ставки')):
        logger.debug('/coinflip - start')
        if self.utils.is_active_game(ctx.author.id):
            embed = set_active_game(ctx, 'Сыграть в монетку')
            await ctx.response.send_message(embed=embed, ephemeral=True)
        else:
            if await get_balance(ctx.author.id) >= amount * 2:
                self.utils.start_game(ctx.author.id)

                embed = set_coinflip(ctx, amount)
                await ctx.response.send_message(embed=embed, view=CoinflipView(ctx, amount, self.utils))
            else:
                embed = set_invalid_money(ctx, 'Сыграть в монетку', await get_balance(ctx.author.id))
                await ctx.response.send_message(embed=embed, ephemeral=True)
    
    # duel
    @commands.slash_command(name='duel', description='Сыграть дуэль', guild_ids=[guild_id])
    async def duel(self, ctx, amount: int = commands.Param(description='Введите сумму ставки'), 
                   opponent: disnake.Member = commands.Param(default=None, description='Выберите оппонента')):
        logger.debug('/duel - start')
        if self.utils.is_active_game(ctx.author.id):
            embed = set_active_game(ctx, 'Сыграть дуэль')
            await ctx.response.send_message(embed=embed, ephemeral=True)
        else:
            if await get_balance(ctx.author.id) >= amount * 2:
                # duel with opponent
                if opponent is not None:
                    # exception
                    if opponent.id == ctx.author.id:
                        embed = set_invalid_user(ctx, 'Сыграть дуэль', 'себя')
                        await ctx.response.send_message(embed=embed, ephemeral=True)
                        return
                    elif opponent.bot:
                        embed = set_invalid_user(ctx, 'Сыграть дуэль', 'бота')
                        await ctx.response.send_message(embed=embed, ephemeral=True)
                        return

                    self.utils.start_game(ctx.author.id)
                    embed = set_duel(ctx, opponent, amount)
                    await ctx.response.send_message(embed=embed, view=DuelView(ctx, opponent, amount, self.utils))
                else:
                    # duel with someone
                    self.utils.start_game(ctx.author.id)
                    embed = set_duel(ctx, opponent, amount)
                    await ctx.response.send_message(embed=embed, view=DuelView(ctx, opponent, amount, self.utils))
            else:
                embed = set_invalid_money(ctx, 'Сыграть дуэль', await get_balance(ctx.author.id))
                await ctx.response.send_message(embed=embed, ephemeral=True)

def setup(client):
    client.add_cog(Games(client))