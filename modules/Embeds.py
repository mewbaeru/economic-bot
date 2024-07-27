import disnake
from disnake.ext import commands
from disnake import Embed

from datetime import datetime, timedelta
from random import randint

def set_timely_embed(ctx: commands.Context, money: int):
    timely_embed = Embed(title="Ежедневная награда",
                        description=f"{ctx.author.mention}, Вы успешно получили ваши **{money}**!",
                        color=0x2f3136)
    timely_embed.set_footer(text='Возвращайтесь через 24 часа')
    timely_embed.set_thumbnail(url=ctx.author.display_avatar.url)
    return timely_embed

def set_time_left_embed(ctx: commands.Context, time_left: timedelta):
    hours, remainder = divmod(int(time_left.total_seconds()), 3600)
    minutes, _ = divmod(remainder, 60)

    if hours > 0:
        time_left_str = f"`{hours:02d} ч. {minutes:02d} мин.`"
    else:
        time_left_str = f"{minutes:02d} мин.`"

    timely_embed = Embed(title="Ежедневная награда",
                        description=f"{ctx.author.mention}, Вы уже забрали свои монеты!\n Возвращайтесь через {time_left_str}",
                        color=0x2f3136)
    timely_embed.set_thumbnail(url=ctx.author.display_avatar.url)
    return timely_embed