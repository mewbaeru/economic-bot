from disnake import Option
from disnake.ext import commands

from database.requests import get_balance, transfer_money
from modules import *

guild_id = Utils.get_guild_id()

class Give(commands.Cog):
    def __init__(self, client):
        self.client = client
    
    # transer money
    @commands.slash_command(name="give", description="Передать валюту", guild_ids=[guild_id])
    async def give(ctx, member: disnake.Member, amount: int):
        logger.debug('/give - start')
        
        balance = await get_balance(ctx.author.id)
        
        if member.id == ctx.author.id or member.bot:
            return
        
        if balance > amount and amount > 0:
            await transfer_money(ctx.author.id, member.id, amount)
            logger.info(f"{ctx.author.name} передал {member.name} {amount} валюты")

            embed = set_give_money(ctx, member, amount)
            await ctx.response.send_message(embed=embed)
        else:
            embed = set_insufficient_funds(ctx)
            await ctx.response.send_message(embed=embed)

def setup(client):
    client.add_cog(Give(client))