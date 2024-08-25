import asyncio
from disnake import SelectOption, ButtonStyle
from disnake.ui import View, button, Button, UserSelect, StringSelect

from modules.Logger import *
from modules.Embeds import *
from database.requests import add_room, take_money, add_transaction, update_room_name, delete_room, get_room_co_owner, add_co_owner, get_room_owner, delete_co_owner, add_new_owner, is_user_already_owner, update_user_limit, get_balance

from datetime import datetime

# room creation confirmation
class RoomConfirmationView(View):
    def __init__(self, ctx, name, colour, members, total_price, settings_roles, timeout=60):
        super().__init__(timeout=timeout)
        self.ctx = ctx
        self.name = name
        self.colour = colour
        self.members = members
        self.total_price = total_price
        self.settings_roles = settings_roles

    async def on_timeout(self):
        embed = set_invalid_time(self.ctx, 'Создание личной комнаты')
        await self.ctx.send(embed=embed, view=View())
    
    @button(emoji='<:gray_check_mark_mewbae:1276606963203047555>', custom_id='btn_yes')
    async def button_callback_yes(self, button, interaction):
        if interaction.user.id == self.ctx.author.id:
            role = await self.ctx.guild.create_role(name=self.name)
            pos = self.ctx.guild.get_role(self.settings_roles.get('personal_room'))

            await role.edit(position=pos.position - 1, colour=self.colour)
            await self.ctx.author.add_roles(role)

            await add_room(self.ctx.author.id, role.id, self.members)
            await take_money(self.ctx.author.id, self.total_price)

            logger.info(f'/create room - owner: {self.ctx.author.id} - room_id: {role.id}')
            # add new transaction
            await add_transaction(self.ctx.author.id, f'Создание комнаты {role.mention}', -self.total_price, datetime.now())

            embed = set_create_room(self.ctx, role)
            self.stop()
            await interaction.response.edit_message(embed=embed, view=View())
    
    @button(emoji='<:gray_negative_squared_cross_mark:1276606994752737433>', custom_id='btn_no')
    async def button_callback_no(self, button, interaction):
        if interaction.user.id == self.ctx.author.id:
            self.stop()
            await interaction.message.delete()

# room manage
class RoomsEdit(View): 
    def __init__(self, ctx, role, room_name, co_owner, time_pay, members, user_limit, settings_prices, timeout=120): 
        super().__init__(timeout=timeout)
        self.ctx = ctx 
        self.role = role
        self.members = members
        self.co_owner = co_owner
        self.time_pay = time_pay
        self.room_name = room_name
        self.user_limit = user_limit
        self.settings_prices = settings_prices

        self.button_back = Button(label='Отмена', custom_id='btn_back', style=ButtonStyle.red, row=1)
        self.button_back_edit_role = Button(label='Вернуться к управлению', custom_id='btn_back_edit', style=ButtonStyle.primary)
        if not self.ctx.author.id == self.co_owner:
            # add select menu for edit room by owner
            self.select_menu = StringSelect(
                placeholder = '🔎 Выберите действие',
                options = [
                    SelectOption(emoji='<:dot_mewbae:1276887777937588365>', label='Изменить название комнаты', value='change_name_room'),
                    SelectOption(emoji='<:dot_mewbae:1276887777937588365>', label='Изменить название роли', value='change_name_role'),
                    SelectOption(emoji='<:dot_mewbae:1276887777937588365>', label='Изменить цвет роли', value='change_color_role'),
                    SelectOption(emoji='<:dot_mewbae:1276887777937588365>', label='Назначить совладельца', value='appoint_co_owner'),
                    SelectOption(emoji='<:dot_mewbae:1276887777937588365>', label='Убрать совладельца', value='remove_co_owner'),
                    SelectOption(emoji='<:dot_mewbae:1276887777937588365>', label='Выдать доступ', value='give_role'),
                    SelectOption(emoji='<:dot_mewbae:1276887777937588365>', label='Забрать доступ', value='take_role'),
                    SelectOption(emoji='<:dot_mewbae:1276887777937588365>', label='Передать права на комнату', value='tranfer_room'),
                    SelectOption(emoji='<:dot_mewbae:1276887777937588365>', label='Увеличить лимит пользователей', value='increase_limit'),
                    SelectOption(emoji='<:dot_mewbae:1276887777937588365>', label='Удалить комнату', value='delete_room'),
                ]
            )
            self.select_menu.callback = self.select_menu_callback
            self.add_item(self.select_menu)
        else:
            # add select menu for edit room by co-owner
            self.select_menu = StringSelect(
                placeholder = '🔎 Выберите действие',
                options = [
                    SelectOption(emoji='<:dot_mewbae:1276887777937588365>', label='Изменить название комнаты', value='change_name_room'),
                    SelectOption(emoji='<:dot_mewbae:1276887777937588365>', label='Изменить название роли', value='change_name_role'),
                    SelectOption(emoji='<:dot_mewbae:1276887777937588365>', label='Изменить цвет роли', value='change_color_role'),
                    SelectOption(emoji='<:dot_mewbae:1276887777937588365>', label='Выдать доступ', value='give_role'),
                    SelectOption(emoji='<:dot_mewbae:1276887777937588365>', label='Забрать доступ', value='take_role'),
                ]
            )
            self.select_menu.callback = self.select_menu_callback
            self.add_item(self.select_menu)

    async def on_timeout(self):
        return
    
    async def button_callback_back(self, interaction):
        if interaction.user.id == self.ctx.author.id:
            embed = set_edit_room(self.ctx, self.room_name, self.role, self.co_owner, self.time_pay, self.members, self.user_limit, 
                                  self.settings_prices.get('room_create'))
            await interaction.response.edit_message(embed=embed, view=self)
            return
    
    async def select_menu_callback(self, interaction):
        if interaction.user.id == self.ctx.author.id:
            if self.select_menu.values[0] == 'change_name_room':
                await self.change_name_room(interaction)
            elif self.select_menu.values[0] == 'change_name_role':
                await self.change_name_role(interaction)
            elif self.select_menu.values[0] == 'change_color_role':
                await self.change_color_role(interaction)
            elif self.select_menu.values[0] == 'appoint_co_owner':
                await self.appoint_co_owner(interaction)
            elif self.select_menu.values[0] == 'remove_co_owner':
                await self.remove_co_owner(interaction)
            elif self.select_menu.values[0] == 'give_role':
                await self.give_role(interaction)
            elif self.select_menu.values[0] == 'take_role':
                await self.take_role(interaction)
            elif self.select_menu.values[0] == 'tranfer_room':
                await self.tranfer_room(interaction)
            elif self.select_menu.values[0] == 'increase_limit':
                await self.increase_limit(interaction)
            elif self.select_menu.values[0] == 'delete_room':
                await self.delete_room(interaction)
    
    async def change_name_room(self, interaction):
        view = View()

        if interaction.user.id == self.ctx.author.id:
            self.button_back.callback = self.button_callback_back
            view.add_item(self.button_back)

            embed = set_change_name_room(self.ctx, self.room_name)
            await interaction.response.edit_message(embed=embed, view=view)
            await interaction.followup.send("Напишите новое название личной комнаты.", ephemeral=True, delete_after=10)

            try:
                def check(message):
                    return interaction.user == message.author
                message = await self.ctx.bot.wait_for('message', timeout=60.0, check=check)
            except asyncio.TimeoutError:
                embed = set_invalid_time(self.ctx, 'Изменение названия комнаты')
                await interaction.followup.send(embed=embed, view=View())
                return
            
            view_verify = View()

            button_yes_verify = Button(emoji='<:gray_check_mark_mewbae:1276606963203047555>', custom_id='btn_yes_verify')
            button_no_verify = Button(emoji='<:gray_negative_squared_cross_mark:1276606994752737433>', custom_id='btn_no_verify')

            async def button_callback_yes_verify(interaction):
                if interaction.user.id == self.ctx.author.id:
                    if len(message.content) <= 100:
                        view = View()
                        self.button_back_edit_role.callback = self.button_callback_back
                        view.add_item(self.button_back_edit_role)

                        await update_room_name(self.ctx.author.id, 'name', message.content)
                        logger.info(f'/change name room - owner: {self.ctx.author.id} - room_id: {self.role.id} - new_name: {self.room_name}')
                        self.room_name = message.content
                        embed = set_success_change_name_room(self.ctx, message.content)
                        await interaction.response.edit_message(embed=embed, view=view)
                    else:
                        embed = set_error_symbols_change_name(self.ctx)
                        await interaction.send(embed=embed, ephemeral=True, view=View())
                
            button_yes_verify.callback = button_callback_yes_verify
            button_no_verify.callback = self.button_callback_back

            view_verify.add_item(button_yes_verify)
            view_verify.add_item(button_no_verify)

            try:
                if message:
                    await message.delete()
            except disnake.NotFound:
                logger.error('/room manage name - message not found')
            
            embed = set_confirmation_change_name(self.ctx, 'комнаты', message.content)
            await interaction.edit_original_response(embed=embed, view=view_verify)

    async def change_name_role(self, interaction):
        view = View()

        if interaction.user.id == self.ctx.author.id:
            self.button_back.callback = self.button_callback_back
            view.add_item(self.button_back)

            embed = set_change_name_role(self.ctx, self.role)
            await interaction.response.edit_message(embed=embed, view=view)
            await interaction.followup.send("Напишите новое название роли.", ephemeral=True, delete_after=10)

            try:
                def check(message):
                    return interaction.user == message.author
                message = await self.ctx.bot.wait_for('message', timeout=60.0, check=check)
            except asyncio.TimeoutError:
                embed = set_invalid_time(self.ctx, 'Изменение названия роли')
                await interaction.followup.send(embed=embed, view=View())
                return
            
            view_verify = View()

            button_yes_verify = Button(emoji='<:gray_check_mark_mewbae:1276606963203047555>', custom_id='btn_yes_verify')
            button_no_verify = Button(emoji='<:gray_negative_squared_cross_mark:1276606994752737433>', custom_id='btn_no_verify')

            async def button_callback_yes_verify(interaction):
                if interaction.user.id == self.ctx.author.id:
                    if len(message.content) <= 100:
                        view = View()
                        self.button_back_edit_role.callback = self.button_callback_back
                        view.add_item(self.button_back_edit_role)

                        await self.role.edit(name=f'{message.content}')
                        logger.info(f'/change name room role - owner: {self.ctx.author.id} - role_id: {self.role.id} - new_name: {self.role.name}')
                        embed = set_success_change_name_role(self.ctx, self.role)
                        await interaction.response.edit_message(embed=embed, view=view)
                    else:
                        embed = set_error_symbols_change_name(self.ctx)
                        await interaction.send(embed=embed, ephemeral=True, view=View())
                
            button_yes_verify.callback = button_callback_yes_verify
            button_no_verify.callback = self.button_callback_back

            view_verify.add_item(button_yes_verify)
            view_verify.add_item(button_no_verify)

            try:
                if message:
                    await message.delete()
            except disnake.NotFound:
                logger.error('/room manage name role - message not found')
            
            embed = set_confirmation_change_name(self.ctx, 'роли', message.content)
            await interaction.edit_original_response(embed=embed, view=view_verify)
    
    async def change_color_role(self, interaction):
        view = View()

        if interaction.user.id == self.ctx.author.id:
            self.button_back.callback = self.button_callback_back
            view.add_item(self.button_back)

            embed = set_change_color_role(self.ctx, self.role)
            await interaction.response.edit_message(embed=embed, view=view)
            await interaction.followup.send("Напишите новый цвет роли.", ephemeral=True, delete_after=10)

            try:
                def check(message):
                    return interaction.user == message.author
                message = await self.ctx.bot.wait_for('message', timeout=60.0, check=check)
                try:
                    if message:
                        await message.delete()
                        colour = await commands.ColourConverter().convert(self.ctx, message.content)
                except commands.BadColorArgument:
                    embed = set_invalid_change_color_role(self.ctx)
                    await interaction.followup.send(embed=embed, ephemeral=True, view=View())
                    logger.error('/room manage color - non-convertible color')
                    return
                except disnake.NotFound:
                    logger.error('/room manage color - message not found')
                    return
            except asyncio.TimeoutError:
                embed = set_invalid_time(self.ctx, 'Изменение  цвета роли')
                await interaction.followup.send(embed=embed, view=View())
                return
            
            view_verify = View()

            button_yes_verify = Button(emoji='<:gray_check_mark_mewbae:1276606963203047555>', custom_id='btn_yes_verify')
            button_no_verify = Button(emoji='<:gray_negative_squared_cross_mark:1276606994752737433>', custom_id='btn_no_verify')

            async def button_callback_yes_verify(interaction):
                if interaction.user.id == self.ctx.author.id:
                    view = View()
                    self.button_back_edit_role.callback = self.button_callback_back
                    view.add_item(self.button_back_edit_role)
                
                    await self.role.edit(color=colour)
                    logger.info(f'/change color room role - owner: {self.ctx.author.id} - role_id: {self.role.id} - new_color: {colour}')
                    embed = set_success_change_color_role(self.ctx, self.role)
                    await interaction.response.edit_message(embed=embed, view=view)
            
            button_yes_verify.callback = button_callback_yes_verify
            button_no_verify.callback = self.button_callback_back

            view_verify.add_item(button_yes_verify)
            view_verify.add_item(button_no_verify)

            embed = set_confirmation_change_color(self.ctx, message.content)
            await interaction.edit_original_response(embed=embed, view=view_verify)
    
    async def appoint_co_owner(self, interaction):
        view = View()

        if interaction.user.id == self.ctx.author.id:
            self.button_back.callback = self.button_callback_back
            view.add_item(self.button_back)

            # select menu with users
            class SelectUsers(UserSelect):
                def __init__(self, ctx, role, co_owner):
                    super().__init__(placeholder='Выберите пользователя')
                    self.ctx = ctx
                    self.role = role
                    self.co_owner = co_owner
            
                async def callback(self, interaction):
                        user_id = int(interaction.data['values'][0])
                        selected_user = self.ctx.guild.get_member(user_id)

                        if selected_user.bot:
                            embed = set_invalid_user(self.ctx, 'Назначить совладельца комнаты', 'бота')
                            await interaction.send(embed=embed, ephemeral=True, view=View())
                            return
                        elif selected_user is None:
                            embed = set_user_not_found(self.ctx, 'Назначить совладельца комнаты')
                            await interaction.send(embed=embed, ephemeral=True, view=View())
                            return
                        elif user_id == interaction.user.id:
                            embed = set_invalid_user(self.ctx, 'Назначить совладельца комнаты', 'себя')
                            await interaction.send(embed=embed, ephemeral=True, view=View())
                            return
                        elif user_id == self.co_owner:
                            embed = set_user_co_owner(self.ctx)
                            await interaction.send(embed=embed, ephemeral=True, view=View())
                            return
                        elif role := interaction.user.get_role(self.role.id):
                            if selected_user.get_role(role.id):
                                await view_verify(selected_user, interaction)
                            else:
                                embed = set_error_action_with_room(self.ctx, 'Назначить совладельца комнаты')
                                await interaction.send(embed=embed, ephemeral=True, view=View())
                                return
            
            view.add_item(SelectUsers(self.ctx, self.role, self.co_owner))
            co_owner = await get_room_co_owner(self.ctx.author.id)
            if co_owner:
                embed = set_already_co_owner(self.ctx, co_owner)
                await interaction.response.edit_message(embed=embed, view=view)
            else:
                embed = set_choose_co_owner(self.ctx)
                await interaction.response.edit_message(embed=embed, view=view)
            
            async def view_verify(selected_user, interaction):
                view_verify = View()

                button_yes_verify = Button(emoji='<:gray_check_mark_mewbae:1276606963203047555>', custom_id='btn_yes_verify')
                button_no_verify = Button(emoji='<:gray_negative_squared_cross_mark:1276606994752737433>', custom_id='btn_no_verify')

                async def button_callback_yes_verify(interaction):
                    if interaction.user.id == self.ctx.author.id:
                        view = View()
                        self.button_back_edit_role.callback = self.button_callback_back
                        view.add_item(self.button_back_edit_role)

                        await add_co_owner(self.ctx.author.id, selected_user.id)
                        logger.info(f'/room manage appoint co-owner - owner: {self.ctx.author.id} - role_id: {self.role.id} - co-owner: {selected_user.id}')
                        self.co_owner = selected_user.id
                        embed = set_success_appoint_co_owner(self.ctx, selected_user)
                        await interaction.response.edit_message(embed=embed, view=view)

                button_yes_verify.callback = button_callback_yes_verify
                button_no_verify.callback = self.button_callback_back

                view_verify.add_item(button_yes_verify)
                view_verify.add_item(button_no_verify)

                embed = set_confirmation_appoint_co_owner(self.ctx, selected_user)
                await interaction.response.edit_message(embed=embed, view=view_verify)
    
    async def remove_co_owner(self, interaction):
        if interaction.user.id == self.ctx.author.id:
            if await get_room_co_owner(self.ctx.author.id) != 0:
                view_verify = View()

                button_yes_verify = Button(emoji='<:gray_check_mark_mewbae:1276606963203047555>', custom_id='btn_yes_verify')
                button_no_verify = Button(emoji='<:gray_negative_squared_cross_mark:1276606994752737433>', custom_id='btn_no_verify')

                async def button_callback_yes_verify(interaction):
                    if interaction.user.id == self.ctx.author.id:
                        view = View()
                        self.button_back_edit_role.callback = self.button_callback_back
                        view.add_item(self.button_back_edit_role)

                        await delete_co_owner(self.ctx.author.id)
                        logger.info(f'/delete room co-owner - owner: {self.ctx.author.id}')
                        self.co_owner = 0

                        embed = set_success_delete_co_owner(self.ctx)
                        await interaction.response.edit_message(embed=embed, view=view)

                button_yes_verify.callback = button_callback_yes_verify
                button_no_verify.callback = self.button_callback_back

                view_verify.add_item(button_yes_verify)
                view_verify.add_item(button_no_verify)

                embed = set_confirmation_delete_co_owner(self.ctx, await get_room_co_owner(self.ctx.author.id))
                await interaction.response.edit_message(embed=embed, view=view_verify)
            else:
                view = View()
                self.button_back.callback = self.button_callback_back
                view.add_item(self.button_back)
                embed = set_not_co_owner(self.ctx)
                await interaction.response.edit_message(embed=embed, view=view)

    async def give_role(self, interaction):
        view = View()

        if interaction.user.id == self.ctx.author.id:
            self.button_back.callback = self.button_callback_back
            view.add_item(self.button_back)

            # select menu with users
            class SelectUsers(UserSelect):
                def __init__(self, ctx, role):
                    super().__init__(placeholder='Выберите пользователя')
                    self.ctx = ctx
                    self.role = role
            
                async def callback(self, interaction):
                        user_id = int(interaction.data['values'][0])
                        selected_user = self.ctx.guild.get_member(user_id)

                        if selected_user.bot:
                            embed = set_invalid_user(self.ctx, 'Выдача доступа в комнату', 'бота')
                            await interaction.send(embed=embed, ephemeral=True, view=View())
                            return
                        elif selected_user is None:
                            embed = set_user_not_found(self.ctx, 'Выдача доступа в комнату')
                            await interaction.send(embed=embed, ephemeral=True, view=View())
                            return
                        elif user_id == interaction.user.id:
                            embed = set_invalid_user(self.ctx, 'Выдача доступа в комнату', 'себя')
                            await interaction.send(embed=embed, ephemeral=True, view=View())
                            return
                        elif role := interaction.user.get_role(self.role.id):
                            if selected_user.get_role(role.id):
                                embed = set_error_already_have_role(self.ctx)
                                await interaction.send(embed=embed, ephemeral=True, view=View())
                                return
                            else:
                                await view_verify(selected_user, interaction)

        users_with_role = len(self.role.members)
        if users_with_role >= int(self.user_limit):
            embed = set_not_give_user_room(self.ctx, self.user_limit)
            await interaction.response.edit_message(embed=embed, view=view)
        else:
            view.add_item(SelectUsers(self.ctx, self.role))
            embed = set_give_user_room(self.ctx, int(self.user_limit)-users_with_role)
            await interaction.response.edit_message(embed=embed, view=view)

        async def view_verify(selected_user, interaction):
            view_verify = View()

            button_yes_verify = Button(emoji='<:gray_check_mark_mewbae:1276606963203047555>', custom_id='btn_yes_verify')
            button_no_verify = Button(emoji='<:gray_negative_squared_cross_mark:1276606994752737433>', custom_id='btn_no_verify')

            async def button_callback_yes_verify(interaction):
                if interaction.user.id == self.ctx.author.id:
                    view = View()
                    self.button_back_edit_role.callback = self.button_callback_back
                    view.add_item(self.button_back_edit_role)
                    
                    await selected_user.add_roles(self.role)
                    logger.info(f'/room manage give - owner: {self.ctx.author.id} - role_id: {self.role.id} - new_user: {selected_user.id}')
                    self.members.append(selected_user)
                    embed = set_success_give_room(self.ctx, selected_user)
                    await interaction.response.edit_message(embed=embed, view=view)

            button_yes_verify.callback = button_callback_yes_verify
            button_no_verify.callback = self.button_callback_back

            view_verify.add_item(button_yes_verify)
            view_verify.add_item(button_no_verify)

            embed = set_confirmation_give_room(self.ctx, selected_user)
            await interaction.response.edit_message(embed=embed, view=view_verify)
    
    async def take_role(self, interaction):
        view = View()

        if interaction.user.id == self.ctx.author.id:
            self.button_back.callback = self.button_callback_back
            view.add_item(self.button_back)

            # select menu with users
            class SelectUsers(UserSelect):
                def __init__(self, ctx, role):
                    super().__init__(placeholder='Выберите пользователя')
                    self.ctx = ctx
                    self.role = role

                async def callback(self, interaction):
                        user_id = int(interaction.data['values'][0])
                        selected_user = self.ctx.guild.get_member(user_id)

                        if selected_user.bot:
                            embed = set_invalid_user(self.ctx, 'Забрать доступ в комнату', 'бота')
                            await interaction.send(embed=embed, ephemeral=True, view=View())
                            return
                        elif selected_user is None:
                            embed = set_user_not_found(self.ctx, 'Забрать доступ в комнату')
                            await interaction.send(embed=embed, ephemeral=True, view=View())
                            return
                        elif user_id == interaction.user.id:
                            embed = set_invalid_user(self.ctx, 'Забрать доступ в комнату', 'себя')
                            await interaction.send(embed=embed, ephemeral=True, view=View())
                            return
                        elif user_id == await get_room_owner(self.ctx.author.id):
                            embed = set_invalid_room_owner(self.ctx)
                            await interaction.send(embed=embed, ephemeral=True, view=View())
                            return
                        elif role := interaction.user.get_role(self.role.id):
                            if not selected_user.get_role(role.id):
                                embed = set_error_have_role(self.ctx)
                                await interaction.send(embed=embed, ephemeral=True, view=View())
                                return
                            else:
                                await view_verify(selected_user, interaction)

        users_with_role = len(self.role.members)
        if users_with_role == 1:
            embed = set_not_user_with_room_role(self.ctx)
            await interaction.response.edit_message(embed=embed, view=view)
        else:
            view.add_item(SelectUsers(self.ctx, self.role))
            embed = set_take_user_room(self.ctx)
            await interaction.response.edit_message(embed=embed, view=view)

        async def view_verify(selected_user, interaction):
            view_verify = View()

            button_yes_verify = Button(emoji='<:gray_check_mark_mewbae:1276606963203047555>', custom_id='btn_yes_verify')
            button_no_verify = Button(emoji='<:gray_negative_squared_cross_mark:1276606994752737433>', custom_id='btn_no_verify')

            async def button_callback_yes_verify(interaction):
                if interaction.user.id == self.ctx.author.id:
                    view = View()
                    self.button_back_edit_role.callback = self.button_callback_back
                    view.add_item(self.button_back_edit_role)
                
                    await selected_user.remove_roles(self.role)
                    logger.info(f'/room manage take - owner: {self.ctx.author.id} - role_id: {self.role.id} - user: {selected_user.id}')
                    self.members.remove(selected_user)
                    embed = set_success_take_room(self.ctx, selected_user)
                    await interaction.response.edit_message(embed=embed, view=view)

            button_yes_verify.callback = button_callback_yes_verify
            button_no_verify.callback = self.button_callback_back

            view_verify.add_item(button_yes_verify)
            view_verify.add_item(button_no_verify)

            embed = set_confirmation_take_room(self.ctx, selected_user)
            await interaction.response.edit_message(embed=embed, view=view_verify)
    
    async def tranfer_room(self, interaction):
        view = View()

        if interaction.user.id == self.ctx.author.id:
            self.button_back.callback = self.button_callback_back
            view.add_item(self.button_back)

            # select menu with users
            class SelectUsers(UserSelect):
                def __init__(self, ctx, role):
                    super().__init__(placeholder='Выберите пользователя')
                    self.ctx = ctx
                    self.role = role

                async def callback(self, interaction):
                    user_id = int(interaction.data['values'][0])
                    selected_user = self.ctx.guild.get_member(user_id)

                    if selected_user.bot:
                        embed = set_invalid_user(self.ctx, 'Передать права на комнату', 'бота')
                        await interaction.send(embed=embed, ephemeral=True, view=View())
                        return
                    elif selected_user is None:
                        embed = set_user_not_found(self.ctx, 'Передать права на комнату')
                        await interaction.send(embed=embed, ephemeral=True, view=View())
                        return
                    elif user_id == interaction.user.id:
                        embed = set_invalid_user(self.ctx, 'Передать права на комнату', 'себя')
                        await interaction.send(embed=embed, ephemeral=True, view=View())
                        return
                    elif await is_user_already_owner(selected_user.id):
                        embed = set_user_already_room(self.ctx, selected_user)
                        await interaction.send(embed=embed, ephemeral=True, view=View())
                    elif role := interaction.user.get_role(self.role.id):
                        if selected_user.get_role(role.id):
                            await view_verify(selected_user, interaction)
                        else:
                            embed = set_error_action_with_room(self.ctx, 'Передать права на комнату')
                            await interaction.send(embed=embed, ephemeral=True, view=View())
                            return
        
        view.add_item(SelectUsers(self.ctx, self.role))
        embed = set_transfer_room(self.ctx)
        await interaction.response.edit_message(embed=embed, view=view)

        async def view_verify(selected_user, interaction):
            view_verify = View()

            button_yes_verify = Button(emoji='<:gray_check_mark_mewbae:1276606963203047555>', custom_id='btn_yes_verify')
            button_no_verify = Button(emoji='<:gray_negative_squared_cross_mark:1276606994752737433>', custom_id='btn_no_verify')

            async def button_callback_yes_verify(interaction):
                if interaction.user.id == self.ctx.author.id:
                    await add_new_owner(self.ctx.author.id, selected_user.id)
                    logger.info(f'/room manage transfer - new_owner: {selected_user.id} - role_id: {self.role.id} - old_owner: {self.ctx.author.id}')
                    embed = set_success_transfer_room(self.ctx, selected_user)
                    await interaction.response.edit_message(embed=embed, view=View())

            button_yes_verify.callback = button_callback_yes_verify
            button_no_verify.callback = self.button_callback_back

            view_verify.add_item(button_yes_verify)
            view_verify.add_item(button_no_verify)

            embed = set_confirmation_transfer_room(self.ctx, selected_user)
            await interaction.response.edit_message(embed=embed, view=view_verify)
    
    async def increase_limit(self, interaction):
        view = View()
        max_limit_reached = True

        async def button_callback_buy_limit(interaction, limit, value):
            if await get_balance(self.ctx.author.id) >= value:
                view = View()
                self.button_back_edit_role.callback = self.button_callback_back
                view.add_item(self.button_back_edit_role)
            
                await update_user_limit(self.ctx.author.id, limit)
                await take_money(self.ctx.author.id, value)

                logger.info(f'/room manage limit - owner: {self.ctx.author.id} - role_id: {self.role.id} - new_limit: {limit}')
                # add new transaction
                await add_transaction(self.ctx.author.id, f'Увеличение слотов в личной комнате до {limit}', -value, datetime.now())

                self.user_limit = limit

                embed = set_success_buy_user_limit(self.ctx, limit, value)
                await interaction.response.edit_message(embed=embed, view=view)
            else:
                embed = set_invalid_money(self.ctx, 'Увеличение слотов в личной комнате', await get_balance(self.ctx.author.id))
                await interaction.send(embed=embed, ephemeral=True, view=View())
                return
            
        if interaction.user.id == self.ctx.author.id:
            users_limit = self.settings_prices.get('users_limit')
            for limit, value in users_limit.items():
                if int(limit) > int(self.user_limit):
                    max_limit_reached = False
                    button_buy_limit = Button(label=f"{limit}", style=ButtonStyle.primary)
                    button_buy_limit.callback = lambda i=interaction, l=limit, v=value: button_callback_buy_limit(i, l, v)
                    view.add_item(button_buy_limit)
            
            if max_limit_reached:
                self.button_back.callback = self.button_callback_back
                view.add_item(self.button_back)
                embed = set_max_user_limit(self.ctx)
                await interaction.response.edit_message(embed=embed, view=view)
            else:
                embed = set_buy_user_limit(self.ctx)
                await interaction.response.edit_message(embed=embed, view=view)
            
    async def delete_room(self, interaction):
        if interaction.user.id == self.ctx.author.id:
            view_verify = View()

            button_yes_verify = Button(emoji='<:gray_check_mark_mewbae:1276606963203047555>', custom_id='btn_yes_verify')
            button_no_verify = Button(emoji='<:gray_negative_squared_cross_mark:1276606994752737433>', custom_id='btn_no_verify')

            async def button_callback_yes_verify(interaction):
                if interaction.user.id == self.ctx.author.id:
                    await delete_room(self.ctx.author.id)
                    await self.role.delete()
                    logger.info(f'/delete room - owner: {self.ctx.author.id}')

                    embed = set_success_delete_room(self.ctx)
                    await interaction.response.edit_message(embed=embed, view=View())

            button_yes_verify.callback = button_callback_yes_verify
            button_no_verify.callback = self.button_callback_back

            view_verify.add_item(button_yes_verify)
            view_verify.add_item(button_no_verify)

            embed = set_confirmation_delete_room(self.ctx)
            await interaction.response.edit_message(embed=embed, view=view_verify)

# room info
class RoomsInfo(View):
    def __init__(self, ctx, role, owner, members, co_owner, time_pay, room_name, timeout=60):
        super().__init__(timeout=timeout)
        self.ctx = ctx
        self.role = role
        self.owner = owner
        self.members = members
        self.co_owner = co_owner
        self.time_pay = time_pay
        self.room_name = room_name
    
        self.select_menu = StringSelect(
            placeholder = '🔎 Выберите меню',
            options = [
                SelectOption(emoji='<:dot_mewbae:1276887777937588365>', label='Основная информация', value='main_info'),
                SelectOption(emoji='<:dot_mewbae:1276887777937588365>', label='Участники', value='members_info'),
            ]
        )
        self.select_menu.callback = self.select_menu_callback
        self.add_item(self.select_menu)
    
    async def on_timeout(self):
        return
    
    async def select_menu_callback(self, interaction):
        if interaction.user.id == self.ctx.author.id:
            if self.select_menu.values[0] == 'main_info':
                await self.main_info(interaction)
            elif self.select_menu.values[0] == 'members_info':
                await self.members_info(interaction)
    
    async def main_info(self, interaction):
        if interaction.user.id == self.ctx.author.id:
            embed = set_info_room(self.ctx, self.room_name, self.role, self.owner, self.co_owner, self.time_pay, len(self.members))
            await interaction.response.edit_message(embed=embed, view=self)
    
    async def members_info(self, interaction):
        if interaction.user.id == self.ctx.author.id:
            embed = set_info_members_room(self.ctx, self.room_name, self.members, self.owner, self.co_owner)
            await interaction.response.edit_message(embed=embed, view=self)