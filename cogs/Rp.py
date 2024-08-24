import disnake
from disnake.ext import commands

from database.requests import get_top_user_balance, get_top_user_online, get_top_user_messages, get_top_marriage_online, get_top_personal_room_online
from modules import *

guild_id = Utils.get_guild_id()

class Rp(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.utils = Utils
    
    # role play
    @commands.slash_command(name='rp', description='Социальные команды', guild_ids=[guild_id])
    async def rp(self, ctx, member: disnake.Member = commands.Param(description='Введите пользователя, которому хотите перевести валюту'), 
                 act: str = commands.Param(description='Выберите действие', choices=[
                     'Поцеловать в губы',
                     'Поцеловать в щеку',
                     'Обнять',
                     'Прижаться',
                     'Спать',
                     'Щекотать',
                     'Погладить',
                     'Подмигнуть',
                     'Поднять',
                     'Улыбнуться',
                     'Смущаться',
                     'Тыкнуть',
                     'Укусить',
                     'Покормить',
                     'Обижаться',
                     'Злиться',
                     'Дать пощечину',
                     'Ударить',
                 ])):
        logger.debug('/rp - start')

        if act == 'Поцеловать в губы':
            random_gif_path = self.utils.get_random_gif('kiss_on_lips')
            embed = set_rp(ctx, member, 'целует', 'себя', '', disnake.File(random_gif_path))
            await ctx.response.send_message(embed=embed)
        elif act == 'Поцеловать в щеку':
            random_gif_path = self.utils.get_random_gif('kiss_on_check')
            embed = set_rp(ctx, member, 'целует', 'себя', '', disnake.File(random_gif_path))
            await ctx.response.send_message(embed=embed)
        elif act == 'Обнять':
            random_gif_path = self.utils.get_random_gif('hug')
            embed = set_rp(ctx, member, 'обнимает', 'себя', '', disnake.File(random_gif_path))
            await ctx.response.send_message(embed=embed)
        elif act == 'Прижаться':
            random_gif_path = self.utils.get_random_gif('cuddle')
            embed = set_rp(ctx, member, 'прижимается', 'к себе', 'к', disnake.File(random_gif_path))
            await ctx.response.send_message(embed=embed)
        elif act == 'Спать':
            random_gif_path = self.utils.get_random_gif('sleep')
            embed = set_rp(ctx, member, 'спит', '', 'с', disnake.File(random_gif_path))
            await ctx.response.send_message(embed=embed)
        elif act == 'Щекотать':
            random_gif_path = self.utils.get_random_gif('tickle')
            embed = set_rp(ctx, member, 'щекочет', 'себя', '', disnake.File(random_gif_path))
            await ctx.response.send_message(embed=embed)
        elif act == 'Погладить':
            random_gif_path = self.utils.get_random_gif('pat')
            embed = set_rp(ctx, member, 'гладит', 'себя', '', disnake.File(random_gif_path))
            await ctx.response.send_message(embed=embed)
        elif act == 'Подмигнуть':
            random_gif_path = self.utils.get_random_gif('wink')
            embed = set_rp(ctx, member, 'подмигивает', '', '', disnake.File(random_gif_path))
            await ctx.response.send_message(embed=embed)
        elif act == 'Поднять':
            random_gif_path = self.utils.get_random_gif('pick up')
            embed = set_rp(ctx, member, 'поднимает', 'себя', '', disnake.File(random_gif_path))
            await ctx.response.send_message(embed=embed)
        elif act == 'Улыбнуться':
            random_gif_path = self.utils.get_random_gif('smiles')
            embed = set_rp(ctx, member, 'улыбается', '', '', disnake.File(random_gif_path))
            await ctx.response.send_message(embed=embed)
        elif act == 'Смущаться':
            random_gif_path = self.utils.get_random_gif('embarrasse')
            embed = set_rp(ctx, member, 'смущается', '', 'из-за', disnake.File(random_gif_path))
            await ctx.response.send_message(embed=embed)
        elif act == 'Тыкнуть':
            random_gif_path = self.utils.get_random_gif('poke')
            embed = set_rp(ctx, member, 'тыкает', 'себя', '', disnake.File(random_gif_path))
            await ctx.response.send_message(embed=embed)
        elif act == 'Укусить':
            random_gif_path = self.utils.get_random_gif('bite')
            embed = set_rp(ctx, member, 'кусает', 'себя', '', disnake.File(random_gif_path))
            await ctx.response.send_message(embed=embed)
        elif act == 'Покормить':
            random_gif_path = self.utils.get_random_gif('feed')
            embed = set_rp(ctx, member, 'кормит', 'себя', '', disnake.File(random_gif_path))
            await ctx.response.send_message(embed=embed)
        elif act == 'Обижаться':
            random_gif_path = self.utils.get_random_gif('take_offense')
            embed = set_rp(ctx, member, 'обижается', '', 'на', disnake.File(random_gif_path))
            await ctx.response.send_message(embed=embed)
        elif act == 'Злиться':
            random_gif_path = self.utils.get_random_gif('get_angry')
            embed = set_rp(ctx, member, 'злится', '', 'на', disnake.File(random_gif_path))
            await ctx.response.send_message(embed=embed)
        elif act == 'Дать пощечину':
            random_gif_path = self.utils.get_random_gif('slap')
            embed = set_rp(ctx, member, 'дает пощечину', 'себе', '', disnake.File(random_gif_path))
            await ctx.response.send_message(embed=embed)
        elif act == 'Ударить':
            random_gif_path = self.utils.get_random_gif('hit')
            embed = set_rp(ctx, member, 'ударяет', 'себя', '', disnake.File(random_gif_path))
            await ctx.response.send_message(embed=embed)

def setup(client):
    client.add_cog(Rp(client))