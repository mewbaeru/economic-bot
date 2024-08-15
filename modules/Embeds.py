import disnake
from disnake.ext import commands
from disnake import Embed

from datetime import timedelta

# error
def set_invalid_money(ctx: commands.Context, action: str, balance: int):
    error_embed = Embed(title=f"{action}",
                        description=f"{ctx.author.mention}, На Вашем счету недостаточно средств для осуществления операции!",
                        color=0x2f3136)
    error_embed.set_footer(text=f"Ваш баланс на данный момент составляет {balance} монет")
    return error_embed

def set_invalid_money_member(member: disnake.Member, action: str, balance: int):
    error_embed = Embed(title=f"{action}",
                        description=f"{member.mention}, На Вашем счету недостаточно средств для осуществления операции!",
                        color=0x2f3136)
    error_embed.set_footer(text=f"Ваш баланс на данный момент составляет {balance} монет")
    return error_embed

def set_invalid_user(ctx: commands.Context, action: str, user: str):
    error_embed = Embed(title=f"{action}",
                        description=f"{ctx.author.mention}, Вы не можете выбрать {user} для выполнения операции!",
                        color=0x2f3136)
    return error_embed

def set_user_not_found(ctx: commands.Context, action: str):
    error_embed = Embed(title=f"{action}",
                        description=f"{ctx.author.mention}, пользователь не найден!",
                        color=0x2f3136)
    return error_embed

def set_invalid_time(ctx: commands.Context, action: str):
    error_embed = Embed(description=f"{ctx.author.mention}, время ожидания истекло!",
                        color=0x2f3136)
    error_embed.set_author(name=f"{ctx.guild.name} | {action}", icon_url=ctx.guild.icon.url)
    error_embed.set_thumbnail(url=ctx.author.display_avatar.url)
    return error_embed

# timely embeds
def set_timely_embed(ctx: commands.Context, money: int):
    timely_embed = Embed(description=f"{ctx.author.mention}, Вы успешно получили ваши **{money}** <:coin_mewbae:1272661482991124481>!",
                        color=0x2f3136)
    timely_embed.set_author(name=f"{ctx.guild.name} | Ежедневная награда", icon_url=ctx.guild.icon.url)
    timely_embed.set_footer(text="Возвращайтесь через 24 часа")
    timely_embed.set_thumbnail(url=ctx.author.display_avatar.url)
    return timely_embed

def set_time_left_embed(ctx: commands.Context, time_left: timedelta):
    hours, remainder = divmod(int(time_left.total_seconds()), 3600)
    minutes, _ = divmod(remainder, 60)

    if hours > 0:
        time_left_str = f"`{hours:02d} ч. {minutes:02d} мин.`"
    else:
        time_left_str = f"`{minutes:02d} мин.`"

    timely_embed = Embed(description=f"{ctx.author.mention}, Вы уже забрали свои монеты!\n Возвращайтесь через {time_left_str}",
                        color=0x2f3136)
    timely_embed.set_author(name=f"{ctx.guild.name} | Ежедневная награда", icon_url=ctx.guild.icon.url)
    timely_embed.set_thumbnail(url=ctx.author.display_avatar.url)
    return timely_embed

# give money embeds
def set_give_money(ctx: commands.Context, member: disnake.Member, amount: int):
    give_embed = Embed(description=f"{ctx.author.mention}, Вы **успешно** перевели **{amount}** <:coin_mewbae:1272661482991124481> {member.mention}!",
                       color=0x2f3136)
    give_embed.set_author(name=f"{ctx.guild.name} | Перевод валюты", icon_url=ctx.guild.icon.url)
    give_embed.set_thumbnail(url=ctx.author.display_avatar.url)
    return give_embed

# personal roles embeds
# create role
def set_invalid_color(ctx: commands.Context):
    personal_roles_embed = Embed(title="Создание роли",
                                 description=f"{ctx.author.id}, Введите **цвет** в корректном **HEX** формате.\nНапример: **#FFFFFF**",
                                 color=0x2f3136)
    return personal_roles_embed

def set_create_role_timeout(ctx: commands.Context):
    personal_roles_embed = Embed(description=f"Время ожидания истекло!",
                                 color=0x2f3136)
    personal_roles_embed.set_author(name=f"{ctx.guild.name} | Создание роли", icon_url=ctx.guild.icon.url)
    personal_roles_embed.set_thumbnail(url=ctx.author.display_avatar.url)
    return personal_roles_embed

def set_role_creation_confirmation(ctx: commands.Context, role_name: str, color: str, cost_role_create: int):
    personal_roles_embed = Embed(description=f"{ctx.author.mention}, Вы уверены, что хотите создать роль `{role_name}` за {cost_role_create} <:coin_mewbae:1272661482991124481>?",
                                 color=color)
    personal_roles_embed.set_author(name=f"{ctx.guild.name} | Создание роли", icon_url=ctx.guild.icon.url)
    personal_roles_embed.set_thumbnail(url=ctx.author.display_avatar.url)
    return personal_roles_embed

def set_create_role(ctx: commands.Context, role: disnake.role):
    personal_roles_embed = Embed(description=f"{ctx.author.mention}, Вы **успешно** создали личную роль {role.mention}!",
                                 color=0x2f3136)
    personal_roles_embed.set_author(name=f"{ctx.guild.name} | Создание роли", icon_url=ctx.guild.icon.url)
    personal_roles_embed.set_thumbnail(url=ctx.author.display_avatar.url)
    return personal_roles_embed

# manage role
def set_manage_role(ctx: commands.Context):
    personal_roles_embed = Embed(description=f"{ctx.author.mention}, выберите роль для **взаимодействия**.",
                                 color=0x2f3136)
    personal_roles_embed.set_author(name=f"{ctx.guild.name} | Управление личной ролью", icon_url=ctx.guild.icon.url)
    personal_roles_embed.set_thumbnail(url=ctx.author.display_avatar.url)
    return personal_roles_embed

def set_edit_role(ctx: commands.Context, role: disnake.role, give_by_user: list, time_pay: int, cost_role_create: int, shop_status: bool, shop_cost: int):
    members_with_role = ', '.join(give_by_user) if give_by_user != 0 else "нет пользователей с этой ролью"

    personal_roles_embed = Embed(description=f"**Название роли:** {role.mention};\n**Цвет роли:** `{role.color}`;\n" \
                                 f"**Выдана пользователям:** {members_with_role};\n**Время оплаты:** <t:{time_pay}>.",
                                 color=0x2f3136)
    personal_roles_embed.add_field(name=f"**Добавлена в магазин**", value=f"```{'Да' if shop_status else 'Нет'}```", inline=True)
    if shop_status is True:
        personal_roles_embed.add_field(name=f"**Стоимость роли**", value=f"```{shop_cost}```", inline=True)
    personal_roles_embed.set_author(name=f"{ctx.guild.name} | Управление личной ролью", icon_url=ctx.guild.icon.url)
    personal_roles_embed.set_footer(text=f"Не забудьте положить на счет стоимость личной роли ({cost_role_create}) до следующего дня оплаты")
    personal_roles_embed.set_thumbnail(url=ctx.author.display_avatar.url)
    return personal_roles_embed

def set_not_roles(ctx: commands.Context):
    personal_roles_embed = Embed(title="Управление личной ролью",
                                 description=f"{ctx.author.mention}, у Вас нет персональных ролей.",
                                 color=0x2f3136)
    personal_roles_embed.set_thumbnail(url=ctx.author.display_avatar.url)
    return personal_roles_embed

def set_change_name_role(ctx: commands.Context, role: disnake.role):
    personal_roles_embed = Embed(description=f"{ctx.author.mention}, введите новое название для роли {role.mention}.",
                                 color=0x2f3136)
    personal_roles_embed.set_author(name=f"{ctx.guild.name} | Изменение названия роли", icon_url=ctx.guild.icon.url)
    personal_roles_embed.set_thumbnail(url=ctx.author.display_avatar.url)
    return personal_roles_embed

def set_confirmation_change_name_role(ctx: commands.Context, role_name: str, cost_role_change_name: int):
    personal_roles_embed = Embed(description=f"{ctx.author.mention}, Вы уверены, что хотите **изменить название** роли на `{role_name}` "
                                 f"за {cost_role_change_name} <:coin_mewbae:1272661482991124481>?",
                                 color=0x2f3136)
    personal_roles_embed.set_author(name=f"{ctx.guild.name} | Изменение названия роли", icon_url=ctx.guild.icon.url)
    personal_roles_embed.set_thumbnail(url=ctx.author.display_avatar.url)
    return personal_roles_embed

def set_success_change_name_role(ctx: commands.Context, role: disnake.role):
    personal_roles_embed = Embed(description=f"{ctx.author.mention}, Вы **успешно** изменили название роли {role.mention}.",
                                 color=0x2f3136)
    personal_roles_embed.set_author(name=f"{ctx.guild.name} | Изменение названия роли", icon_url=ctx.guild.icon.url)
    personal_roles_embed.set_thumbnail(url=ctx.author.display_avatar.url)
    return personal_roles_embed

def set_error_symbols_change_name_role(ctx: commands.Context, role: disnake.role):
    personal_roles_embed = Embed(title=f"Изменение названия роли",
                                 description=f"{ctx.author.mention}, количество символов **не должно превышать 100** для изменения названия роли {role.mention}.",
                                 color=0x2f3136)
    personal_roles_embed.set_thumbnail(url=ctx.author.display_avatar.url)
    return personal_roles_embed

def set_change_color_role(ctx: commands.Context, role: disnake.role):
    personal_roles_embed = Embed(description=f"{ctx.author.mention}, выберите **новый цвет** в формате HEX _(#ffffff)_ для роли {role.mention}.",
                                 color=0x2f3136)
    personal_roles_embed.set_author(name=f"{ctx.guild.name} | Изменение цвета роли", icon_url=ctx.guild.icon.url)
    personal_roles_embed.set_thumbnail(url=ctx.author.display_avatar.url)
    return personal_roles_embed

def set_confirmation_change_color_role(ctx: commands.Context, role_color: str, cost_role_change_color: int):
    personal_roles_embed = Embed(description=f"{ctx.author.mention}, Вы уверены, что хотите **изменить цвет** роли на `{role_color}` "
                                 f"за {cost_role_change_color} <:coin_mewbae:1272661482991124481>?",
                                 color=0x2f3136)
    personal_roles_embed.set_author(name=f"{ctx.guild.name} | Изменение цвета роли", icon_url=ctx.guild.icon.url)
    personal_roles_embed.set_thumbnail(url=ctx.author.display_avatar.url)
    return personal_roles_embed

def set_success_change_color_role(ctx:commands.Context, role: disnake.role):
    personal_roles_embed = Embed(description=f"{ctx.author.mention}, Вы **успешно** изменили цвет своей роли {role.mention}.",
                                 color=0x2f3136)
    personal_roles_embed.set_author(name=f"{ctx.guild.name} | Изменение цвета роли", icon_url=ctx.guild.icon.url)
    personal_roles_embed.set_thumbnail(url=ctx.author.display_avatar.url)
    return personal_roles_embed

def set_invalid_change_color_role(ctx: commands.Context):
    personal_roles_embed = Embed(title=f"Изменение цвета роли",
                                 description=f"{ctx.author.mention}, необходимо ввести цвет в формате HEX _(#ffffff)_.",
                                 color=0x2f3136)
    personal_roles_embed.set_thumbnail(url=ctx.author.display_avatar.url)
    return personal_roles_embed

def set_give_user_role(ctx: commands.Context, role: disnake.role, users_with_role: int):
    personal_roles_embed = Embed(description=f"{ctx.author.mention}, выберите **пользователя**, которому Вы хотите **выдать роль** {role.mention}.",
                                 color=0x2f3136)
    personal_roles_embed.set_author(name=f"{ctx.guild.name} | Выдача роли пользователю", icon_url=ctx.guild.icon.url)
    personal_roles_embed.set_footer(text=f"Вы можете выдать роль только 3 пользователям")
    personal_roles_embed.set_thumbnail(url=ctx.author.display_avatar.url)

    if users_with_role == 2:
        personal_roles_embed.set_footer(text="Вы можете выдать роль только 1 пользователю")
    elif users_with_role == 1:
        personal_roles_embed.set_footer(text="Вы можете выдать роль только 2 пользователям")

    return personal_roles_embed

def set_not_give_user_role(ctx: commands.Context):
    personal_roles_embed = Embed(description=f"{ctx.author.mention}, к сожалению, Вы можете **выдать роль** только 3 пользователям.",
                                 color=0x2f3136)
    personal_roles_embed.set_author(name=f"{ctx.guild.name} | Выдача роли пользователю", icon_url=ctx.guild.icon.url)
    personal_roles_embed.set_thumbnail(url=ctx.author.display_avatar.url)
    return personal_roles_embed

def set_confirmation_give_role(ctx: commands.Context, role: disnake.role, member: disnake.Member):
    personal_roles_embed = Embed(description=f"{ctx.author.mention}, Вы уверены, что хотите **выдать роль** {role.mention} пользователю {member.mention}?",
                                 color=0x2f3136)
    personal_roles_embed.set_author(name=f"{ctx.guild.name} | Выдача роли пользователю", icon_url=ctx.guild.icon.url)
    personal_roles_embed.set_thumbnail(url=ctx.author.display_avatar.url)
    return personal_roles_embed

def set_success_give_role(ctx: commands.Context, role: disnake.role, member: disnake.Member):
    personal_roles_embed = Embed(description=f"{ctx.author.mention}, Вы **успешно** выдали свою роль {role.mention} пользователю {member.mention}.",
                                 color=0x2f3136)
    personal_roles_embed.set_author(name=f"{ctx.guild.name} | Выдача роли пользователю", icon_url=ctx.guild.icon.url)
    personal_roles_embed.set_thumbnail(url=ctx.author.display_avatar.url)
    return personal_roles_embed

def set_take_user_role(ctx: commands.Context, role: disnake.role):
    personal_roles_embed = Embed(description=f"{ctx.author.mention}, выберите **пользователя**, у которого Вы хотите **забрать роль** {role.mention}.",
                                 color=0x2f3136)
    personal_roles_embed.set_author(name=f"{ctx.guild.name} | Забрать роль у пользователя", icon_url=ctx.guild.icon.url)
    personal_roles_embed.set_thumbnail(url=ctx.author.display_avatar.url)
    return personal_roles_embed

def set_take_not_user_role(ctx: commands.Context, role: disnake.role):
    personal_roles_embed = Embed(description=f"{ctx.author.mention}, нет **пользователей**, у которых есть роль {role.mention}.",
                                 color=0x2f3136)
    personal_roles_embed.set_author(name=f"{ctx.guild.name} | Забрать роль у пользователя", icon_url=ctx.guild.icon.url)
    personal_roles_embed.set_thumbnail(url=ctx.author.display_avatar.url)
    return personal_roles_embed

def set_error_already_have_role(ctx: commands.Context):
    personal_roles_embed = Embed(title=f"Выдача роли пользователю",
                                 description=f"{ctx.author.mention}, у выбранного Вами пользователя уже есть эта роль.",
                                 color=0x2f3136)
    return personal_roles_embed

def set_confirmation_take_role(ctx: commands.Context, role: disnake.role, member: disnake.Member):
    personal_roles_embed = Embed(description=f"{ctx.author.mention}, Вы уверены, что хотите **забрать роль** {role.mention} у пользователя {member.mention}?",
                                 color=0x2f3136)
    personal_roles_embed.set_author(name=f"{ctx.guild.name} | Забрать роль у пользователя", icon_url=ctx.guild.icon.url)
    personal_roles_embed.set_thumbnail(url=ctx.author.display_avatar.url)
    return personal_roles_embed

def set_success_take_role(ctx: commands.Context, role: disnake.role, member: disnake.Member):
    personal_roles_embed = Embed(description=f"{ctx.author.mention}, Вы **успешно** забрали свою роль {role.mention} у пользователя {member.mention}.",
                                 color=0x2f3136)
    personal_roles_embed.set_author(name=f"{ctx.guild.name} | Забрать роль у пользователя", icon_url=ctx.guild.icon.url)
    personal_roles_embed.set_thumbnail(url=ctx.author.display_avatar.url)
    return personal_roles_embed

def set_error_have_role(ctx: commands.Context):
    personal_roles_embed = Embed(title=f"Забрать роль у пользователя",
                                 description=f"{ctx.author.mention}, у выбранного Вами пользователя нет этой роли.",
                                 color=0x2f3136)
    return personal_roles_embed

def set_confirmation_delete_role(ctx: commands.Context, role: disnake.role):
    personal_roles_embed = Embed(description=f"{ctx.author.mention}, Вы уверены, что хотите **удалить роль** {role.mention}?",
                                 color=0x2f3136)
    personal_roles_embed.set_author(name=f"{ctx.guild.name} | Удаление роли", icon_url=ctx.guild.icon.url)
    personal_roles_embed.set_footer(text='Возврат средств, потраченных на роль, не осуществляется')
    personal_roles_embed.set_thumbnail(url=ctx.author.display_avatar.url)
    return personal_roles_embed

def set_success_delete_role(ctx: commands.Context):
    personal_roles_embed = Embed(description=f"{ctx.author.mention}, Вы **успешно** удалили свою роль.",
                                 color=0x2f3136)
    personal_roles_embed.set_author(name=f"{ctx.guild.name} | Удаление роли", icon_url=ctx.guild.icon.url)
    personal_roles_embed.set_thumbnail(url=ctx.author.display_avatar.url)
    return personal_roles_embed

def set_add_role_to_shop(ctx: commands.Context, role: disnake.role):
    personal_roles_embed = Embed(description=f"{ctx.author.mention}, введите стоимость роли {role.mention} для добавления ее в магазин.",
                                 color=0x2f3136)
    personal_roles_embed.set_author(name=f"{ctx.guild.name} | Добавление роли в магазин", icon_url=ctx.guild.icon.url)
    personal_roles_embed.set_thumbnail(url=ctx.author.display_avatar.url)
    return personal_roles_embed

def set_confirmation_add_role_to_shop(ctx: commands.Context, role: disnake.role, role_cost: int):
    personal_roles_embed = Embed(description=f"{ctx.author.mention}, Вы уверены, что хотите **добавить роль** {role.mention} в магазин со стоимостью {role_cost} <:coin_mewbae:1272661482991124481>?",
                                 color=0x2f3136)
    personal_roles_embed.set_author(name=f"{ctx.guild.name} | Добавление роли в магазин", icon_url=ctx.guild.icon.url)
    personal_roles_embed.set_thumbnail(url=ctx.author.display_avatar.url)
    return personal_roles_embed

def set_success_add_role_to_shop(ctx: commands.Context, role: disnake.role, role_cost: int):
    personal_roles_embed = Embed(description=f"{ctx.author.mention}, Вы **успешно** добавили свою роль {role.mention} со стоимостью {role_cost} <:coin_mewbae:1272661482991124481> в магазин.",
                                 color=0x2f3136)
    personal_roles_embed.set_author(name=f"{ctx.guild.name} | Добавление роли в магазин", icon_url=ctx.guild.icon.url)
    personal_roles_embed.set_thumbnail(url=ctx.author.display_avatar.url)
    return personal_roles_embed

def set_role_already_in_shop(ctx: commands.Context, role: disnake.role):
    personal_roles_embed = Embed(description=f"{ctx.author.mention}, Ваша роль {role.mention} уже добавлена в магазин.",
                                 color=0x2f3136)
    personal_roles_embed.set_author(name=f"{ctx.guild.name} | Добавление роли в магазин", icon_url=ctx.guild.icon.url)
    personal_roles_embed.set_thumbnail(url=ctx.author.display_avatar.url)
    return personal_roles_embed

def set_change_cost_role(ctx: commands.Context, role: disnake.role):
    personal_roles_embed = Embed(description=f"{ctx.author.mention}, введите новую стоимость роли {role.mention} для магазина.",
                                 color=0x2f3136)
    personal_roles_embed.set_author(name=f"{ctx.guild.name} | Изменение стоимости роли в магазине", icon_url=ctx.guild.icon.url)
    personal_roles_embed.set_thumbnail(url=ctx.author.display_avatar.url)
    return personal_roles_embed

def set_confirmation_change_cost_role(ctx: commands.Context, role: disnake.role, new_role_cost: int):
    personal_roles_embed = Embed(description=f"{ctx.author.mention}, Вы уверены, что хотите **изменить стоимость роли** {role.mention} в магазине на стоимость {new_role_cost} <:coin_mewbae:1272661482991124481>?",
                                 color=0x2f3136)
    personal_roles_embed.set_author(name=f"{ctx.guild.name} | Изменение стоимости роли в магазине", icon_url=ctx.guild.icon.url)
    personal_roles_embed.set_thumbnail(url=ctx.author.display_avatar.url)
    return personal_roles_embed

def set_success_change_cost_role(ctx: commands.Context, role: disnake.role, new_role_cost: int):
    personal_roles_embed = Embed(description=f"{ctx.author.mention}, Вы **успешно** изменили стоимость роли {role.mention} на {new_role_cost} <:coin_mewbae:1272661482991124481>.",
                                 color=0x2f3136)
    personal_roles_embed.set_author(name=f"{ctx.guild.name} | Изменение стоимости роли в магазине", icon_url=ctx.guild.icon.url)
    personal_roles_embed.set_thumbnail(url=ctx.author.display_avatar.url)
    return personal_roles_embed

def set_invalid_role_shop(ctx: commands.Context, action: str):
    personal_roles_embed = Embed(description=f"{ctx.author.mention}, Ваша роль еще не добавлена в магазин.",
                                 color=0x2f3136)
    personal_roles_embed.set_author(name=f"{ctx.guild.name} | {action}", icon_url=ctx.guild.icon.url)
    personal_roles_embed.set_thumbnail(url=ctx.author.display_avatar.url)
    return personal_roles_embed

def set_invalid_cost_role(ctx: commands.Context, action: str):
    personal_roles_embed = Embed(title=f"{action}",
                                 description=f"{ctx.author.mention}, необходимо ввести стоимость роли от **500** до **3000**.",
                                 color=0x2f3136)
    personal_roles_embed.set_thumbnail(url=ctx.author.display_avatar.url)
    return personal_roles_embed

def set_confirmation_delete_role_from_shop(ctx: commands.Context, role: disnake.role):
    personal_roles_embed = Embed(description=f"{ctx.author.mention}, Вы уверены, что хотите **удалить роль** {role.mention} из магазина?.",
                                 color=0x2f3136)
    personal_roles_embed.set_author(name=f"{ctx.guild.name} | Удаление роли из магазина", icon_url=ctx.guild.icon.url)
    personal_roles_embed.set_thumbnail(url=ctx.author.display_avatar.url)
    return personal_roles_embed

def set_success_delete_role_from_shop(ctx: commands.Context):
    personal_roles_embed = Embed(description=f"{ctx.author.mention}, Ваша роль **успешно удалена** из магазина.",
                                 color=0x2f3136)
    personal_roles_embed.set_author(name=f"{ctx.guild.name} | Удаление роли из магазина", icon_url=ctx.guild.icon.url)
    personal_roles_embed.set_thumbnail(url=ctx.author.display_avatar.url)
    return personal_roles_embed

# games
def set_active_game(ctx: commands.Context, game_name: str):
    game_embed = Embed(description=f"{ctx.author.mention}, у вас уже есть активная игра.",
                       color=0x2f3136)
    game_embed.set_author(name=f"{ctx.guild.name} | {game_name}", icon_url=ctx.guild.icon.url)
    game_embed.set_thumbnail(url=ctx.author.display_avatar.url)
    return game_embed

# coinflip
def set_coinflip(ctx: commands.Context, amount: int):
    game_embed = Embed(description=f"{ctx.author.mention}, выберите сторону, на которую хотите поставить {amount} <:coin_mewbae:1272661482991124481>.",
                       color=0x2f3136)
    game_embed.set_author(name=f"{ctx.guild.name} | Сыграть в монетку", icon_url=ctx.guild.icon.url)
    game_embed.set_thumbnail(url=ctx.author.display_avatar.url)
    return game_embed

def set_process_coinflip(ctx: commands.Context, chosen_side: str, amount: int):
    game_embed = Embed(description=f"**Ставка:** {amount} <:coin_mewbae:1272661482991124481>;\n**Выбранная сторона:** {chosen_side}.",
                       color=0x2f3136)
    game_embed.set_author(name=f"{ctx.guild.name} | Сыграть в монетку", icon_url=ctx.guild.icon.url)
    game_embed.set_footer(text=f'Играет: {ctx.author.name}', icon_url=ctx.user.avatar.url)
    return game_embed

def set_win_coinflip(ctx: commands.Context, amount: int, balance: int):
    game_embed = Embed(description=f"{ctx.author.mention}, выпал орел.\nПоздравляем, Вы **выиграли** {amount * 2} <:coin_mewbae:1272661482991124481>!",
                       color=0x2f3136)
    game_embed.set_author(name=f"{ctx.guild.name} | Сыграть в монетку", icon_url=ctx.guild.icon.url)
    game_embed.set_footer(text=f'Ваш баланс на данных момент составляет: {balance} монет')
    game_embed.set_thumbnail(url=ctx.author.display_avatar.url)
    return game_embed

def set_lose_coinflip(ctx: commands.Context, amount: int, balance: int):
    game_embed = Embed(title=f"Сыграть в монетку",
                       description=f"{ctx.author.mention}, выпала решка.\nК сожалению, Вы **проиграли** {amount} <:coin_mewbae:1272661482991124481>.",
                       color=0x2f3136)
    game_embed.set_author(name=f"{ctx.guild.name} | Сыграть в монетку", icon_url=ctx.guild.icon.url)
    game_embed.set_footer(text=f'Ваш баланс на данных момент составляет: {balance} монет')
    game_embed.set_thumbnail(url=ctx.author.display_avatar.url)
    return game_embed

# duel
def set_duel(ctx: commands.Context, member_id: disnake.Member, amount: int):
    if member_id is not None:
        text_game = f"{ctx.author.mention}, хочет поиграть против {member_id.mention} на {amount} <:coin_mewbae:1272661482991124481>."
    else:
        text_game = f"{ctx.author.mention}, хочет поиграть с кем-нибудь на {amount} <:coin_mewbae:1272661482991124481>."

    game_embed = Embed(description=f"{text_game}",
                       color=0x2f3136)
    game_embed.set_author(name=f"{ctx.guild.name} | Сыграть дуэль", icon_url=ctx.guild.icon.url)
    game_embed.set_thumbnail(url=ctx.author.display_avatar.url)
    return game_embed

def set_process_duel(ctx: commands.Context, member_id: disnake.Member, amount: int):
    game_embed = Embed(description=f"{member_id.mention} принимает дуэль от {ctx.author.mention};\n**Ставка:** {amount} <:coin_mewbae:1272661482991124481>.",
                       color=0x2f3136)
    game_embed.set_author(name=f"{ctx.guild.name} | Дуэль: {ctx.author.name} vs {member_id.name}", icon_url=ctx.guild.icon.url)
    game_embed.set_footer(text=f'Бросил(а) вызов: {ctx.author.name}', icon_url=ctx.user.avatar.url)
    return game_embed

def set_win_duel(ctx: commands.Context, winner: disnake.Member, loser: disnake.Member, amount: int):
    game_embed = Embed(description=f"{winner.mention}, **выигрывает** дуэль и получает {amount * 2} <:coin_mewbae:1272661482991124481>!",
                       color=0x2f3136)
    game_embed.set_author(name=f"{ctx.guild.name} | Дуэль: {winner.name} vs {loser.name}", icon_url=ctx.guild.icon.url)
    game_embed.set_footer(text=f'Бросил(а) вызов: {ctx.author.name}', icon_url=ctx.user.avatar.url)
    game_embed.set_thumbnail(url=winner.display_avatar.url)
    return game_embed

# balance
def set_balance_user(ctx: commands.Context, member_id: disnake.Member, balance: int):
    balance_embed = Embed(color=0x2f3136)
    balance_embed.set_author(name=f"{ctx.guild.name} | Текущий баланс — {member_id.name}", icon_url=ctx.guild.icon.url)
    balance_embed.add_field(name="Монеты пользователя:", value=f"```{balance}```")
    balance_embed.set_thumbnail(url=member_id.display_avatar.url)
    return balance_embed

# transaction
def set_transaction(ctx: commands.Context, user: disnake.Member, transactions: list, page: int, total_pages: int):
    page_transactions = transactions[(page-1)*10:page*10]

    transaction_embed = Embed(color=0x2f3136)
    description = ''
    
    for category, value, time in page_transactions:
        description += f"◦ {value} <:coin_mewbae:1272661482991124481> — <t:{time}> — {category}\n\n"
    
    transaction_embed.description = description
    transaction_embed.set_author(name=f"{ctx.guild.name} | Транзакции — {user.name}", icon_url=ctx.guild.icon.url)
    transaction_embed.set_thumbnail(url=user.display_avatar.url)
    transaction_embed.set_footer(text=f"Страница {page} из {total_pages}")
    return transaction_embed

def set_not_transaction(ctx: commands.Context):
    transaction_embed = Embed(title=f"Посмотреть транзакции",
                              description=f"{ctx.author.mention}, у пользователя еще нет транзакций.",
                              color=0x2f3136)
    transaction_embed.set_thumbnail(url=ctx.author.display_avatar.url)
    return transaction_embed

# shop
def set_shop(ctx: commands.Context, roles: list, page: int, total_pages: int):
    page_roles = roles[(page-1)*5:page*5]

    shop_embed = Embed(color=0x2f3136)
    description = ''
    
    for i, (role_id, time, owner_id, price, count) in enumerate(page_roles):
        description += f"**{i+1}.** <@&{role_id}>\n**Продавец:** <@{owner_id}>\n**Цена:** {price} <:coin_mewbae:1272661482991124481>\n**Покупок:** {count}\n\n"

    shop_embed.description = description
    shop_embed.set_author(name=f"{ctx.guild.name} | Магазин ролей", icon_url=ctx.guild.icon.url)
    shop_embed.set_footer(text=f"Страница {page} из {total_pages}")
    shop_embed.set_thumbnail(url=ctx.author.display_avatar.url)
    return shop_embed

def set_empty_shop(ctx: commands.Context):
    shop_embed = Embed(description=f"К сожалению, магазин ролей на данный момент пуст.",
                       color=0x2f3136)
    shop_embed.set_author(name=f"{ctx.guild.name} | Магазин ролей", icon_url=ctx.guild.icon.url)
    shop_embed.set_thumbnail(url=ctx.author.display_avatar.url)
    return shop_embed

def set_already_have_role(ctx: commands.Context):
    shop_embed = Embed(title=f"Магазин ролей",
                       description=f"{ctx.author.mention}, у Вас уже есть данная роль.",
                       color=0x2f3136)
    shop_embed.set_thumbnail(url=ctx.author.display_avatar.url)
    return shop_embed

def set_confirmation_buy_role(ctx: commands.Context, role: disnake.role, role_cost: int):
    shop_embed = Embed(description=f"{ctx.author.mention}, Вы уверены, что хотите **купить роль** {role.mention} за {role_cost} <:coin_mewbae:1272661482991124481>.",
                       color=0x2f3136)
    shop_embed.set_author(name=f"{ctx.guild.name} | Приобретение роли", icon_url=ctx.guild.icon.url)
    shop_embed.set_thumbnail(url=ctx.author.display_avatar.url)
    return shop_embed

def set_success_buy_role(ctx: commands.Context, role: disnake.role, role_cost: int):
    shop_embed = Embed(description=f"{ctx.author.mention}, Вы **успешно** купили роль {role.mention} за {role_cost} <:coin_mewbae:1272661482991124481>.",
                       color=0x2f3136)
    shop_embed.set_author(name=f"{ctx.guild.name} | Приобретение роли", icon_url=ctx.guild.icon.url)
    shop_embed.set_thumbnail(url=ctx.author.display_avatar.url)
    return shop_embed

def set_another_shop(ctx: commands.Context, price: int, page: int, total_pages: int):
    shop_embed = Embed(description=f"**1.** Доступ отправлять картинки в чат\n**Цена:** {price} <:coin_mewbae:1272661482991124481>",
                       color=0x2f3136)
    shop_embed.set_author(name=f"{ctx.guild.name} | Дополнительный магазин", icon_url=ctx.guild.icon.url)
    shop_embed.set_footer(text=f"Страница {page} из {total_pages}")
    shop_embed.set_thumbnail(url=ctx.author.display_avatar.url)
    return shop_embed

def set_confirmation_buy_additional_role(ctx: commands.Context, role: disnake.role, role_cost: int):
    shop_embed = Embed(description=f"{ctx.author.mention}, Вы уверены, что хотите **купить роль** <@&{role}> за {role_cost} <:coin_mewbae:1272661482991124481>.",
                       color=0x2f3136)
    shop_embed.set_author(name=f"{ctx.guild.name} | Приобретение роли", icon_url=ctx.guild.icon.url)
    shop_embed.set_thumbnail(url=ctx.author.display_avatar.url)
    return shop_embed

def set_success_buy_additional_role(ctx: commands.Context, role: int,  role_cost: int):
    shop_embed = Embed(description=f"{ctx.author.mention}, Вы **успешно** купили роль <@&{role}> за {role_cost} <:coin_mewbae:1272661482991124481>.",
                       color=0x2f3136)
    shop_embed.set_author(name=f"{ctx.guild.name} | Приобретение роли", icon_url=ctx.guild.icon.url)
    shop_embed.set_thumbnail(url=ctx.author.display_avatar.url)
    return shop_embed

# marry
def set_marry(ctx: commands.Context, member: disnake.Member):
    marry_embed = Embed(description=f"{ctx.author.mention} отправил предложение о заключении брака {member.mention}.",
                        color=0x2f3136)
    marry_embed.set_author(name=f"{ctx.guild.name} | Заключить брак", icon_url=ctx.guild.icon.url)
    marry_embed.set_thumbnail(url=ctx.author.display_avatar.url)
    return marry_embed

def set_active_marry(ctx: commands.Context):
    marry_embed = Embed(title='Заключить брак',
                        description=f"{ctx.author.mention}, Вы уже находитесь в браке.",
                        color=0x2f3136)
    marry_embed.set_author(name=f"{ctx.guild.name} | Заключить брак", icon_url=ctx.guild.icon.url)
    marry_embed.set_thumbnail(url=ctx.author.display_avatar.url)
    return marry_embed

def set_active_marry_member(ctx: commands.Context, member: disnake.Member):
    marry_embed = Embed(title='Заключить брак',
                        description=f"{ctx.author.mention}, к сожалению, {member.mention} уже находится в браке.",
                        color=0x2f3136)
    marry_embed.set_thumbnail(url=ctx.author.display_avatar.url)
    return marry_embed

def set_refusal_wedding(ctx: commands.Context, member: disnake.Member):
    marry_embed = Embed(description=f"{ctx.author.mention}, к сожалению, {member.mention} отказался заключать брак с Вами.",
                        color=0x2f3136)
    marry_embed.set_author(name=f"{ctx.guild.name} | Заключить брак", icon_url=ctx.guild.icon.url)
    marry_embed.set_thumbnail(url=ctx.author.display_avatar.url)
    return marry_embed

def set_success_marry(ctx: commands.Context, member: disnake):
    marry_embed = Embed(description=f"{ctx.author.mention} и {member.mention} теперь в браке!",
                       color=0x2f3136)
    marry_embed.set_author(name=f"{ctx.guild.name} | Заключить брак", icon_url=ctx.guild.icon.url)
    marry_embed.set_thumbnail(url=ctx.author.display_avatar.url)
    return marry_embed