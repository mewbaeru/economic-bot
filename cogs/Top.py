from disnake import Option
from disnake.ext import commands

from database.requests import get_top_user_balance, get_top_user_online, get_top_user_messages, get_top_marriage_online, get_top_personal_room_online
from modules import *

from datetime import datetime, timedelta

guild_id = Utils.get_guild_id()

class Top(commands.Cog):
    def __init__(self, client):
        self.client = client
    
    # top
    @commands.slash_command(name='top', description='Лучшие пользователи сервера', guild_ids=[guild_id],
                            options=[
                                Option(name='category', description='Выберите тип топа', required=True, choices=[
                                    'Баланс',
                                    'Онлайн',
                                    'Сообщения',
                                    'Браки',
                                    'Личные комнаты',
                                ])
                            ])
    async def top(self, ctx, category):
        logger.debug('/top - start')
        if category == 'Баланс':
            top, author_rank = await get_top_user_balance(ctx.author.id)
            embed = set_top_balance(ctx, top, author_rank)
            await ctx.response.send_message(embed=embed)
        elif category == 'Онлайн':
            top, author_rank = await get_top_user_online(ctx.author.id)
            embed = set_top_online(ctx, top, author_rank)
            await ctx.response.send_message(embed=embed)
        elif category == 'Сообщения':
            top, author_rank = await get_top_user_messages(ctx.author.id)
            embed = set_top_messages(ctx, top, author_rank)
            await ctx.response.send_message(embed=embed)
        elif category == 'Браки':
                top, author_rank = await get_top_marriage_online(ctx.author.id)
                if top is not None:
                    embed = set_top_marriage(ctx, top, author_rank)
                    await ctx.response.send_message(embed=embed)
                else:
                    embed = set_not_top(ctx)
                    await ctx.response.send_message(embed=embed, ephemeral=True)
        elif category == 'Личные комнаты':
            top, author_rank = await get_top_personal_room_online(ctx.author.id)
            if top is not None:
                embed = set_top_personal_room(ctx, top, author_rank)
                await ctx.response.send_message(embed=embed)
            else:
                embed = set_not_top(ctx)
                await ctx.response.send_message(embed=embed, ephemeral=True)

def setup(client):
    client.add_cog(Top(client))