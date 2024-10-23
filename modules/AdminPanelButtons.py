from disnake import ButtonStyle
from disnake.ui import View, button, Button, Select

from modules.Logger import *
from modules.Embeds import *
from database.requests import  get_balance, is_exists_role, get_all_roles_users, is_exists_room, get_personal_room_data, get_info_room, give_money, add_transaction, take_money, add_role, delete_role, add_room, is_exists_room_owner, update_room_name, delete_room

# main menu admin panel
class AdminPanelView(View):
    def __init__(self, ctx, member, settings_roles, timeout=30):
        super().__init__(timeout=timeout)
        self.ctx = ctx
        self.member = member
        self.settings_roles = settings_roles
    
    async def on_timeout(self):
        return
    
    @button(label='Валюта', custom_id='btn_manipulate_balance')
    async def button_callback_manipulate_balance(self, button, interaction):
        if self.ctx.author.id == interaction.user.id:
            embed = set_manipulate_balance(self.ctx, self.member, await get_balance(self.member.id))
            await interaction.response.edit_message(embed=embed, view=ManipulateBalanceView(self.ctx, self.member, self.settings_roles))
    
    @button(label='Личные роли', custom_id='btn_manipulate_roles')
    async def button_callback_manipulate_roles(self, button, interaction):
        if self.ctx.author.id == interaction.user.id:
            embed = set_manipulate_roles(self.ctx, self.member)
            await interaction.response.edit_message(embed=embed, view=ManipulateRolesView(self.ctx, self.member, self.settings_roles))

    @button(label='Личные комнаты', custom_id='btn_manipulate_room')
    async def button_callback_manipulate_room(self, button, interaction):
        if self.ctx.author.id == interaction.user.id:
            if await is_exists_room_owner(self.member.id):
                personal_room_data = await get_personal_room_data(self.member.id)
                info_room = await get_info_room(self.member.id)

                role_room = disnake.utils.get(self.ctx.guild.roles, id=info_room[0])

                if personal_room_data['name'] != 0:
                    room_name = personal_room_data['name']
                else:
                    room_name = role_room.name

                embed = set_manipulate_room(self.ctx, self.member, role_room, room_name)
                await interaction.response.edit_message(embed=embed, view=ManipulateRoomView(self.ctx, self.member, role_room, room_name, self.settings_roles))
            else:
                embed = set_not_room_for_manipulate(self.ctx, self.member)
                await interaction.response.edit_message(embed=embed, view=ManipulateRoomView(self.ctx, self.member, None, None, self.settings_roles))
    
    @button(emoji='<:negative_squared_cross_mark_mewb:1276598003699814510>', custom_id='delete_admin_panel', style=ButtonStyle.red)
    async def button_callback_delete_admin_panel(self, button, interaction):
        if interaction.user.id == self.ctx.author.id:
            await interaction.message.delete()

# view with modal
# manipulate balance
class ManipulateBalanceView(View):
    def __init__(self, ctx, member, settings_roles, timeout=30):
        super().__init__(timeout=timeout)
        self.ctx = ctx
        self.member = member
        self.settings_roles = settings_roles

        self.button_back_admin_panel = Button(label='Вернуться к управлению', custom_id='btn_back_panel', style=ButtonStyle.primary)

    async def on_timeout(self):
        return

    async def button_callback_back_panel(self, interaction):
        if interaction.user.id == self.ctx.author.id:
            embed = set_admin_panel(self.ctx, self.member)
            await interaction.response.edit_message(embed=embed, view=AdminPanelView(self.ctx, self.member, self.settings_roles))
            return
        
    @button(label='Выдать валюту', custom_id='btn_give_money')
    async def button_callback_give_money(self, button, interaction):
        if self.ctx.author.id == interaction.user.id:
            class BalanceGiveModal(disnake.ui.Modal):
                def __init__(self, ctx, member, button_callback_back_panel):
                    self.ctx = ctx
                    self.member = member
                    self.button_callback_back_panel = button_callback_back_panel

                    components = [
                        disnake.ui.TextInput(label=f'Выдать валюту {self.member.name}', placeholder='Например: 1000', min_length=1, max_length=15, custom_id='give_money_input')
                    ]
                    super().__init__(title=f'Выдача валюты пользователю', custom_id='give_money_modal', components=components)

                async def callback(self, interaction):
                    amount = int(interaction.text_values['give_money_input'])
                    await give_money(self.member.id, amount)

                    logger.info(f"/admin panel give money - member: {self.member.id} - amount: {amount}")
                    # add new transaction
                    await add_transaction(self.member.id, f'Перевод валюты администратором', +amount, datetime.now())
                    
                    view = View()
                    self.button_back_admin_panel = Button(label='Вернуться к управлению', custom_id='btn_back_panel', style=ButtonStyle.primary)
                    self.button_back_admin_panel.callback = self.button_callback_back_panel
                    view.add_item(self.button_back_admin_panel)

                    embed = set_give_money_by_admin(self.ctx, self.member, amount)
                    await interaction.response.edit_message(embed=embed, view=view)

            await interaction.response.send_modal(BalanceGiveModal(self.ctx, self.member, self.button_callback_back_panel))
    
    @button(label='Снять валюту', custom_id='btn_take_money')
    async def button_callback_take_money(self, button, interaction):
        if self.ctx.author.id == interaction.user.id:
            class BalanceTakeModal(disnake.ui.Modal):
                def __init__(self, ctx, member, button_callback_back_panel):
                    self.ctx = ctx
                    self.member = member
                    self.button_callback_back_panel = button_callback_back_panel

                    components = [
                        disnake.ui.TextInput(label=f'Снять валюту {self.member.name}', placeholder='Например: 1000', min_length=1, max_length=15, custom_id='take_money_input')
                    ]
                    super().__init__(title=f'Снятие валюты пользователя', custom_id='take_money_modal', components=components)
                
                async def callback(self, interaction):
                    amount = int(interaction.text_values['take_money_input'])
                    await take_money(self.member.id, amount)

                    logger.info(f"/admin panel take money - member: {self.member.id} - amount: {amount}")
                    # add new transaction
                    await add_transaction(self.member.id, f'Снятие валюты администратором', -amount, datetime.now())

                    view = View()
                    self.button_back_admin_panel = Button(label='Вернуться к управлению', custom_id='btn_back_panel', style=ButtonStyle.primary)
                    self.button_back_admin_panel.callback = self.button_callback_back_panel
                    view.add_item(self.button_back_admin_panel)

                    embed = set_take_money_by_admin(self.ctx, self.member, amount)
                    await interaction.response.edit_message(embed=embed, view=view)
            
            await interaction.response.send_modal(BalanceTakeModal(self.ctx, self.member, self.button_callback_back_panel))

    @button(label='Отмена', custom_id='btn_back', style=ButtonStyle.red)
    async def button_callback_back(self, button, interaction):
        if interaction.user.id == self.ctx.author.id:
            embed = set_admin_panel(self.ctx, self.member)
            await interaction.response.edit_message(embed=embed, view=AdminPanelView(self.ctx, self.member, self.settings_roles))
            return

# manipulate roles
class ManipulateRolesView(View):
    def __init__(self, ctx, member, settings_roles, timeout=30):
        super().__init__(timeout=timeout)
        self.ctx = ctx
        self.member = member
        self.settings_roles = settings_roles

        self.button_back_admin_panel = Button(label='Вернуться к управлению', custom_id='btn_back_panel', style=ButtonStyle.primary)

    async def on_timeout(self):
        return
    
    async def button_callback_back_panel(self, interaction):
        if interaction.user.id == self.ctx.author.id:
            embed = set_admin_panel(self.ctx, self.member)
            await interaction.response.edit_message(embed=embed, view=AdminPanelView(self.ctx, self.member, self.settings_roles))
            return
        
    @button(label='Создать роль', custom_id='btn_create_role')
    async def button_callback_create_role(self, button, interaction):
        if self.ctx.author.id == interaction.user.id:
            class CreateRoleModal(disnake.ui.Modal):
                def __init__(self, ctx, member, settings_roles, button_back_admin_panel, button_callback_back_panel):
                    self.ctx = ctx
                    self.member = member
                    self.settings_roles = settings_roles
                    self.button_back_admin_panel = button_back_admin_panel
                    self.button_callback_back_panel = button_callback_back_panel

                    components = [
                        disnake.ui.TextInput(label=f'Название роли', placeholder='Например: mewbaeru', min_length=1, max_length=100, custom_id='name_role_input'),
                        disnake.ui.TextInput(label=f'Цвет роли', placeholder='Например: #ffffff', min_length=7, max_length=7, custom_id='color_role_input'),
                    ]
                    super().__init__(title=f'Создание роли', custom_id='give_money_modal', components=components)

                async def callback(self, interaction):
                    role_name = interaction.text_values['name_role_input']
                    role_color = interaction.text_values['color_role_input']

                    view = View()
                    self.button_back_admin_panel.callback = self.button_callback_back_panel
                    view.add_item(self.button_back_admin_panel)

                    try:
                        colour = await commands.ColourConverter().convert(self.ctx, role_color)
                    except Exception:
                        embed = set_invalid_color_for_modal(self.ctx, self.member)
                        await interaction.response.edit_message(embed=embed, view=view)
                        return
                    
                    role = await self.ctx.guild.create_role(name=role_name)
                    pos = self.ctx.guild.get_role(self.settings_roles.get('personal_role'))

                    await role.edit(position=pos.position - 1, colour=colour)
                    await self.member.add_roles(role)

                    await add_role(self.member.id, role.id)

                    logger.info(f"/admin panel create role - member: {self.member.id} - role_id: {role.id}")

                    embed = set_create_role_for_modal(self.ctx, self.member, role)
                    await interaction.response.edit_message(embed=embed, view=view)
        
            await interaction.response.send_modal(CreateRoleModal(self.ctx, self.member, self.settings_roles, self.button_back_admin_panel,
                                                                   self.button_callback_back_panel))
    
    @button(label='Изменить роль', custom_id='btn_edit_role')
    async def button_callback_edit_role(self, button, interaction):
        if self.ctx.author.id == interaction.user.id:
            if await is_exists_role(self.member.id):
                view = View()

                # menu for choose a role
                select_menu = Select(placeholder='Выберите настраиваемую роль', max_values=1)
                roles = await get_all_roles_users(self.member.id)

                for role in roles:
                    n_role = disnake.utils.get(self.ctx.guild.roles, id=role)
                    select_menu.add_option(emoji='<:dot_mewbae:1276887777937588365>', label=f'{n_role.name}', value=f'{n_role.id}')
                
                async def callback(interaction):
                    role = disnake.utils.get(self.ctx.guild.roles, id=int(select_menu.values[0]))

                    view_edit_role = View()

                    button_change_name = Button(label='Изменить название', custom_id='btn_change_name')
                    button_delete_role = Button(label='Удалить роль', custom_id='btn_delete_role')
                    button_back = Button(label='Отмена', custom_id='btn_back_manipulate_role', style=ButtonStyle.red)
                    
                    async def callback_change_name(interaction):
                        if interaction.user.id == self.ctx.author.id:
                            class ChangeNameModal(disnake.ui.Modal):
                                def __init__(self, ctx, role, member, button_back_admin_panel, button_callback_back_panel):
                                    self.ctx = ctx
                                    self.role = role
                                    self.member = member
                                    self.button_back_admin_panel = button_back_admin_panel
                                    self.button_callback_back_panel = button_callback_back_panel

                                    components = [
                                        disnake.ui.TextInput(label=f'Введите новое название роли {self.role.name}', placeholder='Например: mewbaeru', min_length=1, max_length=100, custom_id='name_role_input')
                                    ]
                                    super().__init__(title=f'Изменение названия роли', custom_id='name_role_input', components=components)

                                async def callback(self, interaction):
                                    name_role = str(interaction.text_values['name_role_input'])
                                    await self.role.edit(name=f'{name_role}')

                                    logger.info(f"/admin panel change name role - owner: {self.member.id} - role: {self.role.id} - new_name: {name_role}")

                                    view = View()
                                    self.button_back_admin_panel.callback = self.button_callback_back_panel
                                    view.add_item(self.button_back_admin_panel)

                                    embed = set_change_name_role_by_admin(self.ctx, self.member, self.role)
                                    await interaction.response.edit_message(embed=embed, view=view)
                            
                            await interaction.response.send_modal(ChangeNameModal(self.ctx, role, self.member, self.button_back_admin_panel,
                                                                                  self.button_callback_back_panel))
                    
                    async def callback_delete_role(interaction):
                        if interaction.user.id == self.ctx.author.id:
                            await delete_role(role.id)
                            await role.delete()

                            logger.info(f'/admin panel delete role - owner: {self.member.id} - role: {role.id}')

                            view = View()
                            self.button_back_admin_panel.callback = self.button_callback_back_panel
                            view.add_item(self.button_back_admin_panel)

                            embed = set_delete_role_by_admin(self.ctx, self.member)
                            await interaction.response.edit_message(embed=embed, view=view)
                    
                    async def callback_back_manipulate_role(interaction):
                        if interaction.user.id == self.ctx.author.id:
                            embed = set_manipulate_roles(self.ctx, self.member)
                            await interaction.response.edit_message(embed=embed, view=self)
                            return

                    button_change_name.callback = callback_change_name
                    button_delete_role.callback = callback_delete_role
                    button_back.callback = callback_back_manipulate_role

                    view_edit_role.add_item(button_change_name)
                    view_edit_role.add_item(button_delete_role)
                    view_edit_role.add_item(button_back)

                    embed = set_manipulate_role(self.ctx, self.member, role)
                    await interaction.response.edit_message(embed=embed, view=view_edit_role)

                select_menu.callback = callback
                view.add_item(select_menu)
                embed = set_manipulate_roles(self.ctx, self.member)
                await interaction.response.edit_message(embed=embed, view=view)
            else:
                embed = set_not_roles_for_manipulate(self.ctx, self.member)
                await interaction.response.edit_message(embed=embed, view=View())
    
    @button(label='Отмена', custom_id='btn_back', style=ButtonStyle.red)
    async def button_callback_back(self, button, interaction):
        if interaction.user.id == self.ctx.author.id:
            embed = set_admin_panel(self.ctx, self.member)
            await interaction.response.edit_message(embed=embed, view=AdminPanelView(self.ctx, self.member, self.settings_roles))
            return

class ManipulateRoomView(View):
    def __init__(self, ctx, member, role_room, room_name, settings_roles, timeout=30):
        super().__init__(timeout=timeout)
        self.ctx = ctx
        self.member = member
        self.role_room = role_room
        self.room_name = room_name
        self.settings_roles = settings_roles
        
        button_create_room = Button(label='Создать комнату', custom_id='btn_create_room')
        button_edit_room = Button(label='Изменить комнату', custom_id='btn_edit_room')

        self.button_back = Button(label='Отмена', custom_id='btn_back', style=ButtonStyle.red)
        self.button_back_admin_panel = Button(label='Вернуться к управлению', custom_id='btn_back_panel', style=ButtonStyle.primary)

        if self.role_room is None:
            button_create_room.callback = self.button_callback_create_room
            self.button_back.callback = self.button_callback_back_panel

            self.add_item(button_create_room)
            self.add_item(self.button_back)
        else:
            button_edit_room.callback = self.button_callback_edit_room
            self.button_back.callback = self.button_callback_back_panel

            self.add_item(button_edit_room)
            self.add_item(self.button_back)

    async def on_timeout(self):
        return

    async def button_callback_back_panel(self, interaction):
        if interaction.user.id == self.ctx.author.id:
            embed = set_admin_panel(self.ctx, self.member)
            await interaction.response.edit_message(embed=embed, view=AdminPanelView(self.ctx, self.member, self.settings_roles))
            return

    async def button_callback_create_room(self, interaction):
        if self.ctx.author.id == interaction.user.id:
            class CreateRoomModal(disnake.ui.Modal):
                def __init__(self, ctx, member, room_name, role_room, settings_roles, button_back_admin_panel, button_callback_back_panel):
                    self.ctx = ctx
                    self.member = member
                    self.room_name = room_name
                    self.role_room = role_room
                    self.settings_roles = settings_roles
                    self.button_back_admin_panel = button_back_admin_panel
                    self.button_callback_back_panel = button_callback_back_panel

                    components = [
                        disnake.ui.TextInput(label=f'Название комнаты', placeholder='Например: mewbaeru', min_length=1, max_length=100, custom_id='name_room_input'),
                        disnake.ui.TextInput(label=f'Цвет роли комнаты', placeholder='Например: #ffffff', min_length=7, max_length=7, custom_id='color_role_room_input'),
                        disnake.ui.TextInput(label=f'Лимит пользователей', placeholder='Например: 5, 10, 15, 20', min_length=1, max_length=2, custom_id='limit_users_input')
                    ]
                    super().__init__(title=f'Создание комнаты', custom_id='create_room_modal', components=components)

                async def callback(self, interaction):
                    room_name = str(interaction.text_values['name_room_input'])
                    role_color = interaction.text_values['color_role_room_input']
                    users_limit = int(interaction.text_values['limit_users_input'])

                    view = View()
                    self.button_back_admin_panel.callback = self.button_callback_back_panel
                    view.add_item(self.button_back_admin_panel)

                    # exceptions
                    try:
                        colour = await commands.ColourConverter().convert(self.ctx, role_color)
                    except Exception:
                        embed = set_invalid_color_for_modal(self.ctx, self.member)
                        await interaction.response.edit_message(embed=embed, view=view)
                        return
                    
                    if users_limit not in [5, 10, 15, 20]:
                        embed = set_invalid_users_limit_for_modal(self.ctx, self.member)
                        await interaction.response.edit_message(embed=embed, view=view)
                        return
                    
                    role = await self.ctx.guild.create_role(name=room_name)
                    pos = self.ctx.guild.get_role(self.settings_roles.get('personal_room'))

                    await role.edit(position=pos.position - 1, colour=colour)
                    await self.member.add_roles(role)
                    await add_room(self.member.id, role.id, users_limit)

                    self.room_name = role.name
                    self.role_room = role

                    logger.info(f"/admin panel create room - member: {self.member.id} - role_id: {role.id}")

                    embed = set_create_room_for_modal(self.ctx, self.member, role)
                    await interaction.response.edit_message(embed=embed, view=view)
            
            await interaction.response.send_modal(CreateRoomModal(self.ctx, self.member, self.room_name, self.role_room, self.settings_roles, self.button_back_admin_panel,
                                                                                  self.button_callback_back_panel))
    
    async def button_callback_edit_room(self, interaction):
        view_edit_room = View()

        if self.ctx.author.id == interaction.user.id:
            button_change_name_role = Button(label='Изменить название роли', custom_id='btn_change_name_role')
            button_change_name_room = Button(label='Изменить название комнаты', custom_id='btn_change_name_room')
            button_delete_room = Button(label='Удалить комнату', custom_id='btn_delete_room')

            async def callback_change_name_role(interaction):
                if interaction.user.id == self.ctx.author.id:
                    class ChangeNameRoleModal(disnake.ui.Modal):
                        def __init__(self, ctx, member, role_room, button_back_admin_panel, button_callback_back_panel):
                            self.ctx = ctx
                            self.member = member
                            self.role_room = role_room
                            self.button_back_admin_panel = button_back_admin_panel
                            self.button_callback_back_panel = button_callback_back_panel

                            components = [
                                disnake.ui.TextInput(label=f'Введите новое название роли {self.role_room.name}', placeholder='Например: mewbaeru', min_length=1, max_length=100, custom_id='name_role_input')
                            ]
                            super().__init__(title=f'Изменение названия роли комнаты', custom_id='name_room_role_input', components=components)

                        async def callback(self, interaction):
                            name_role = str(interaction.text_values['name_role_input'])

                            await self.role_room.edit(name=f'{name_role}')

                            logger.info(f"/admin panel change name role room - owner: {self.member.id} - role: {self.role_room.id} - new_name: {name_role}")

                            view = View()
                            self.button_back_admin_panel.callback = self.button_callback_back_panel
                            view.add_item(self.button_back_admin_panel)

                            embed = set_change_name_role_by_admin(self.ctx, self.member, self.role_room)
                            await interaction.response.edit_message(embed=embed, view=view)
                    
                    await interaction.response.send_modal(ChangeNameRoleModal(self.ctx,self.member, self.role_room, self.button_back_admin_panel,
                                                                            self.button_callback_back_panel))

            async def callback_change_name_room(interaction):
                if interaction.user.id == self.ctx.author.id:
                    class ChangeNameRoomModal(disnake.ui.Modal):
                        def __init__(self, ctx, member, role_room, button_back_admin_panel, button_callback_back_panel):
                            self.ctx = ctx
                            self.member = member
                            self.role_room = role_room
                            self.button_back_admin_panel = button_back_admin_panel
                            self.button_callback_back_panel = button_callback_back_panel

                            components = [
                                disnake.ui.TextInput(label=f'Введите новое название комнаты {self.role_room.name}', placeholder='Например: mewbaeru', min_length=1, max_length=100, custom_id='name_room_input')
                            ]
                            super().__init__(title=f'Изменение названия роли комнаты', custom_id='name_room_input', components=components)

                        async def callback(self, interaction):
                            name_role = str(interaction.text_values['name_room_input'])

                            await update_room_name(self.member.id, 'name', name_role)
                            logger.info(f"/admin panel change name room - owner: {self.member.id} - role: {self.role_room.id} - new_name: {name_role}")

                            self.room_name = name_role

                            view = View()
                            self.button_back_admin_panel.callback = self.button_callback_back_panel
                            view.add_item(self.button_back_admin_panel)

                            embed = set_change_name_role_by_admin(self.ctx, self.member, self.role_room)
                            await interaction.response.edit_message(embed=embed, view=view)
                    
                    await interaction.response.send_modal(ChangeNameRoomModal(self.ctx, self.member, self.role_room, self.button_back_admin_panel,
                                                                            self.button_callback_back_panel))

            async def callback_delete_room(interaction):
                if interaction.user.id == self.ctx.author.id:
                    await delete_room(self.member.id)
                    await self.role_room.delete()
                    
                    logger.info(f'/admin panel delete room - owner: {self.member.id} - role: {self.role_room.id}')

                    view = View()
                    self.button_back_admin_panel.callback = self.button_callback_back_panel
                    view.add_item(self.button_back_admin_panel)

                    embed = set_delete_room_by_admin(self.ctx, self.member)
                    await interaction.response.edit_message(embed=embed, view=view)
            
            button_change_name_room.callback = callback_change_name_room
            button_delete_room.callback = callback_delete_room
            button_change_name_role.callback = callback_change_name_role
            self.button_back.callback = self.button_callback_back_panel

            view_edit_room.add_item(button_change_name_room)
            view_edit_room.add_item(button_change_name_role)
            view_edit_room.add_item(button_delete_room)
            view_edit_room.add_item(self.button_back)

            embed = set_manipulate_room(self.ctx, self.member, self.role_room, self.room_name)
            await interaction.response.edit_message(embed=embed, view=view_edit_room)