import disnake
from disnake.ext import commands
from disnake import Embed

from datetime import datetime, timedelta
from random import randint

# timely embeds
def set_timely_embed(ctx: commands.Context, money: int):
    timely_embed = Embed(title="Ежедневная награда",
                        description=f"{ctx.author.mention}, Вы успешно получили ваши **{money}**!",
                        color=0x2f3136)
    timely_embed.set_footer(text="Возвращайтесь через 24 часа")
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

# give money embeds
def set_give_money(ctx: commands.Context, member: disnake.Member, amount: int):
    give_embed = Embed(title="Передать валюту",
                       description=f"{ctx.author.mention}, Вы **успешно** перевели **{amount}** {member.mention}!",
                       color=0x2f3136)
    give_embed.set_thumbnail(url=ctx.author.display_avatar.url)
    return give_embed

def set_insufficient_funds(ctx: commands.Context):
    give_embed = Embed(title="Передать валюту",
                       description=f"{ctx.author.mention}, на Вашем счету недостаточно средств для перевода!",
                       color=0x2f3136)
    give_embed.set_thumbnail(url=ctx.author.display_avatar.url)
    return give_embed

# personal roles embeds
# create role
def set_invalid_color():
    personal_roles_embed = Embed(title="Создание роли",
                                 description=f"Введите **цвет** в корректном **HEX** формате.\nНапример: **#FFFFFF**",
                                 color=0x2f3136)
    return personal_roles_embed

def set_invalid_money():
    personal_roles_embed = Embed(title="Создание роли",
                                 description=f"На Вашем счету недостаточно средств для перевода!",
                                 color=0x2f3136)
    return personal_roles_embed

def set_timeout(ctx: commands.Context):
    personal_roles_embed = Embed(title="Создание роли",
                                 description=f"Время ожидания истекло!",
                                 color=0x2f3136)
    personal_roles_embed.set_thumbnail(url=ctx.author.display_avatar.url)
    return personal_roles_embed

def set_role_creation_confirmation(ctx: commands.Context, role_name: str, color: str, cost_role_create: int):
    personal_roles_embed = Embed(title="Создание роли",
                                 description=f"{ctx.author.mention}, Вы уверены, что хотите создать роль `{role_name}` за {cost_role_create}?",
                                 color=color)
    personal_roles_embed.set_thumbnail(url=ctx.author.display_avatar.url)
    return personal_roles_embed

def set_create_role(ctx: commands.Context, role: disnake.role):
    personal_roles_embed = Embed(title="Создание роли",
                                 description=f"{ctx.author.mention}, Вы **успешно** создали личную роль {role.mention}!",
                                 color=0x2f3136)
    personal_roles_embed.set_thumbnail(url=ctx.author.display_avatar.url)
    return personal_roles_embed

# manage role
def set_manage_role(ctx: commands.Context):
    personal_roles_embed = Embed(title="Создание роли",
                                 description=f"{ctx.author.mention}, выберите роль для **взаимодействия**.",
                                 color=0x2f3136)
    personal_roles_embed.set_thumbnail(url=ctx.author.display_avatar.url)
    return personal_roles_embed

def set_edit_role(ctx: commands.Context, role: disnake.role, time_pay: str, cost_role_create: int):
    time_pay_formatted = time_pay.strftime("%Y-%m-%d")
    members_with_roles = ', '.join([member.mention for member in ctx.guild.members if member != ctx.author and role in member.roles]) or "нет пользователей с этой ролью"

    personal_roles_embed = Embed(title=f"Управление личной ролью",
                                 description=f"**Название роли:** {role.mention};\n**Цвет роли:** `{role.color}`;\n" \
                                 f"**Выдана пользователям:** {members_with_roles};\n**Время оплаты:** `{time_pay_formatted}`.",
                                 color=0x2f3136)
    personal_roles_embed.set_footer(text=f"Не забудьте положить на счет стоимость личной роли ({cost_role_create}) до следующего дня оплаты")
    personal_roles_embed.set_thumbnail(url=ctx.author.display_avatar.url)
    return personal_roles_embed

def set_not_roles(ctx: commands.Context):
    personal_roles_embed = Embed(title=f"Управление личной ролью",
                                 description=f"{ctx.author.mention}, у Вас нет персональных ролей.",
                                 color=0x2f3136)
    personal_roles_embed.set_thumbnail(url=ctx.author.display_avatar.url)
    return personal_roles_embed

def set_change_name_role(ctx: commands.Context, role: disnake.role):
    personal_roles_embed = Embed(title=f"Изменение названия роли",
                                 description=f"{ctx.author.mention}, введите новое название для роли {role.mention}.",
                                 color=0x2f3136)
    personal_roles_embed.set_thumbnail(url=ctx.author.display_avatar.url)
    return personal_roles_embed

def set_change_color_role(ctx: commands.Context, role: disnake.role):
    personal_roles_embed = Embed(title=f"Изменение цвета роли",
                                 description=f"{ctx.author.mention}, выберите **новый цвет** в формате HEX _(#ffffff)_ для роли {role.mention}.",
                                 color=0x2f3136)
    personal_roles_embed.set_thumbnail(url=ctx.author.display_avatar.url)
    return personal_roles_embed

def set_give_user_role(ctx: commands.Context, role: disnake.role):
    personal_roles_embed = Embed(title=f"Выдача роли пользователю",
                                 description=f"{ctx.author.mention}, выберите **пользователя**, которому Вы хотите **выдать роль** {role.mention}.",
                                 color=0x2f3136)
    personal_roles_embed.set_footer(text=f"Вы можете выдать роль только 3 пользователям")
    personal_roles_embed.set_thumbnail(url=ctx.author.display_avatar.url)

    users_with_role = len([member for member in ctx.guild.members if member != ctx.author and role in member.roles])
    if users_with_role >= 3:
        personal_roles_embed = Embed(title=f"Выдача роли пользователю",
                                 description=f"{ctx.author.id}, к сожалению, Вы можете выдать роль только 3 пользователям",
                                 color=0x2f3136)
    elif users_with_role == 2:
        personal_roles_embed.set_footer(text="Вы можете выдать роль только 1 пользователю")
    elif users_with_role == 1:
        personal_roles_embed.set_footer(text="Вы можете выдать роль только 2 пользователям")

    return personal_roles_embed

def set_take_user_role(ctx: commands.Context, role: disnake.role):
    personal_roles_embed = Embed(title=f"Забрать роль у пользователя",
                                 description=f"{ctx.author.mention}, выберите **пользователя**, у которого Вы хотите **забрать роль** {role.mention}.",
                                 color=0x2f3136)
    personal_roles_embed.set_thumbnail(url=ctx.author.display_avatar.url)
    return personal_roles_embed

def set_take_not_user_role(ctx: commands.Context, role: disnake.role):
    personal_roles_embed = Embed(title=f"Забрать роль у пользователя",
                                 description=f"{ctx.author.mention}, нет **пользователей**, у которых есть роль {role.mention}.",
                                 color=0x2f3136)
    personal_roles_embed.set_thumbnail(url=ctx.author.display_avatar.url)
    return personal_roles_embed

def set_confirmation_change_name_role(ctx: commands.Context, role_name: str, cost_role_change_name: int):
    personal_roles_embed = Embed(title=f"Изменение названия роли",
                                 description=f"{ctx.author.mention}, Вы уверены, что хотите **изменить название** роли на `{role_name}` "
                                 f"за {cost_role_change_name}?",
                                 color=0x2f3136)
    personal_roles_embed.set_thumbnail(url=ctx.author.display_avatar.url)
    return personal_roles_embed

def set_confirmation_change_color_role(ctx: commands.Context, role_color: str, cost_role_change_color: int):
    personal_roles_embed = Embed(title=f"Изменение цвета роли",
                                 description=f"{ctx.author.mention}, Вы уверены, что хотите **изменить цвет** роли на `{role_color}` "
                                 f"за {cost_role_change_color}?",
                                 color=0x2f3136)
    personal_roles_embed.set_thumbnail(url=ctx.author.display_avatar.url)
    return personal_roles_embed

def set_confiramtion_give_role(ctx: commands.Context, role: disnake.role, member: disnake.Member):
    personal_roles_embed = Embed(title=f"Выдача роли пользователю",
                                 description=f"{ctx.author.mention}, Вы уверены, что хотите **выдать роль** {role.mention} пользователю {member.mention}?",
                                 color=0x2f3136)
    personal_roles_embed.set_thumbnail(url=ctx.author.display_avatar.url)
    return personal_roles_embed

def set_confiramtion_take_role(ctx: commands.Context, role: disnake.role, member: disnake.Member):
    personal_roles_embed = Embed(title=f"Забрать роль у пользователя",
                                 description=f"{ctx.author.mention}, Вы уверены, что хотите **забрать роль** {role.mention} у пользователя {member.mention}?",
                                 color=0x2f3136)
    personal_roles_embed.set_thumbnail(url=ctx.author.display_avatar.url)
    return personal_roles_embed

def set_confirmation_delete_role(ctx: commands.Context, role: disnake.role):
    personal_roles_embed = Embed(title=f"Удаление роли",
                                 description=f"{ctx.author.mention}, Вы уверены, что хотите **удалить роль** {role.mention}?",
                                 color=0x2f3136)
    personal_roles_embed.set_footer(text='Возврат средств, потраченных на роль, не осуществляется')
    personal_roles_embed.set_thumbnail(url=ctx.author.display_avatar.url)
    return personal_roles_embed

def set_success_change_name_role(ctx: commands.Context, role: disnake.role):
    personal_roles_embed = Embed(title=f"Изменение названия роли",
                                 description=f"{ctx.author.mention}, Вы **успешно** изменили название роли {role.mention}.",
                                 color=0x2f3136)
    personal_roles_embed.set_thumbnail(url=ctx.author.display_avatar.url)
    return personal_roles_embed

def set_success_change_color_role(ctx:commands.Context, role: disnake.role):
    personal_roles_embed = Embed(title=f"Изменение цвета роли",
                                 description=f"{ctx.author.mention}, Вы **успешно** изменили цвет своей роли {role.mention}.",
                                 color=0x2f3136)
    personal_roles_embed.set_thumbnail(url=ctx.author.display_avatar.url)
    return personal_roles_embed

def set_success_give_role(ctx: commands.Context, role: disnake.role, member: disnake.Member):
    personal_roles_embed = Embed(title=f"Выдача роли пользователю",
                                 description=f"{ctx.author.mention}, Вы **успешно** выдали свою роль {role.mention} пользователю {member.mention}.",
                                 color=0x2f3136)
    personal_roles_embed.set_thumbnail(url=ctx.author.display_avatar.url)
    return personal_roles_embed

def set_success_take_role(ctx: commands.Context, role: disnake.role, member: disnake.Member):
    personal_roles_embed = Embed(title=f"Забрать роль у пользователя",
                                 description=f"{ctx.author.mention}, Вы **успешно** забрали свою роль {role.mention} у пользователя {member.mention}.",
                                 color=0x2f3136)
    personal_roles_embed.set_thumbnail(url=ctx.author.display_avatar.url)
    return personal_roles_embed

def set_success_delete_role(ctx: commands.Context):
    personal_roles_embed = Embed(title=f"Удаление роли",
                                 description=f"{ctx.author.mention}, Вы **успешно** удалили свою роль.",
                                 color=0x2f3136)
    personal_roles_embed.set_thumbnail(url=ctx.author.display_avatar.url)
    return personal_roles_embed

def set_invalid_change_role(ctx: commands.Context):
    personal_roles_embed = Embed(title=f"Управление личной ролью",
                                 description=f"{ctx.author.mention}, время ожидания истекло!",
                                 color=0x2f3136)
    personal_roles_embed.set_thumbnail(url=ctx.author.display_avatar.url)
    return personal_roles_embed

def set_error_change_role(ctx: commands.Context, role: disnake.role):
    personal_roles_embed = Embed(title=f"Изменение названия роли",
                                 description=f"{ctx.author.mention}, на Вашем счету **недостаточно средств** для изменения роли {role.mention}.",
                                 color=0x2f3136)
    personal_roles_embed.set_thumbnail(url=ctx.author.display_avatar.url)
    return personal_roles_embed

def set_error_symbols_change_name_role(ctx: commands.Context, role: disnake.role):
    personal_roles_embed = Embed(title=f"Изменение названия роли",
                                 description=f"{ctx.author.mention}, количество символов **не должно превышать 100** для изменения названия роли {role.mention}.",
                                 color=0x2f3136)
    personal_roles_embed.set_thumbnail(url=ctx.author.display_avatar.url)
    return personal_roles_embed

def set_error_bot_give_role(ctx: commands.Context):
    personal_roles_embed = Embed(title=f"Выдача роли пользователю",
                                 description=f"{ctx.author.mention}, Вы не можете выбрать бота для выдачи роли.",
                                 color=0x2f3136)
    personal_roles_embed.set_thumbnail(url=ctx.author.display_avatar.url)
    return personal_roles_embed

def set_error_give_yourself_role(ctx: commands.Context):
    personal_roles_embed = Embed(title=f"Выдача роли пользователю",
                                 description=f"{ctx.author.mention}, Вы не можете выбрать себя для выдачи роли.",
                                 color=0x2f3136)
    personal_roles_embed.set_thumbnail(url=ctx.author.display_avatar.url)
    return personal_roles_embed

def set_error_not_user_give_role(ctx: commands.Context):
    personal_roles_embed = Embed(title=f"Выдача роли пользователю",
                                 description=f"{ctx.author.mention}, выбранный Вами пользователь не найден.",
                                 color=0x2f3136)
    personal_roles_embed.set_thumbnail(url=ctx.author.display_avatar.url)
    return personal_roles_embed

def set_error_already_have_role(ctx: commands.Context):
    personal_roles_embed = Embed(title=f"Выдача роли пользователю",
                                 description=f"{ctx.author.mention}, у выбранного Вами пользователя уже есть эта роль.",
                                 color=0x2f3136)
    personal_roles_embed.set_thumbnail(url=ctx.author.display_avatar.url)
    return personal_roles_embed

def set_error_bot_take_role(ctx: commands.Context):
    personal_roles_embed = Embed(title=f"Забрать роль у пользователя",
                                 description=f"{ctx.author.mention}, Вы не можете выбрать бота для изъятия роли.",
                                 color=0x2f3136)
    personal_roles_embed.set_thumbnail(url=ctx.author.display_avatar.url)
    return personal_roles_embed

def set_error_take_yourself_role(ctx: commands.Context):
    personal_roles_embed = Embed(title=f"Забрать роль у пользователя",
                                 description=f"{ctx.author.mention}, Вы не можете выбрать себя для изъятия роли.",
                                 color=0x2f3136)
    personal_roles_embed.set_thumbnail(url=ctx.author.display_avatar.url)
    return personal_roles_embed

def set_error_not_user_take_role(ctx: commands.Context):
    personal_roles_embed = Embed(title=f"Забрать роль у пользователя",
                                 description=f"{ctx.author.mention}, выбранный Вами пользователь не найден.",
                                 color=0x2f3136)
    personal_roles_embed.set_thumbnail(url=ctx.author.display_avatar.url)
    return personal_roles_embed

def set_error_have_role(ctx: commands.Context):
    personal_roles_embed = Embed(title=f"Забрать роль у пользователя",
                                 description=f"{ctx.author.mention}, у выбранного Вами пользователя нет этой роли.",
                                 color=0x2f3136)
    personal_roles_embed.set_thumbnail(url=ctx.author.display_avatar.url)
    return personal_roles_embed

def set_invalid_change_color_role(ctx: commands.Context):
    personal_roles_embed = Embed(title=f"Изменение цвета роли",
                                 description=f"{ctx.author.mention}, необходимо ввести цвет в формате HEX _(#ffffff)_.",
                                 color=0x2f3136)
    personal_roles_embed.set_thumbnail(url=ctx.author.display_avatar.url)
    return personal_roles_embed