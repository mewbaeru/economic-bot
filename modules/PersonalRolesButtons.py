import asyncio
from disnake import SelectOption
from disnake.ui import View, button, Button, UserSelect, StringSelect

from modules.Logger import *
from modules.Embeds import *
from database.requests import add_role, take_money, get_balance, delete_role, add_transaction, add_role_to_shop, change_cost_role_in_shop, is_exists_role_in_shop, delete_role_from_shop, add_give_by_owner, get_give_by_owner, get_len_user_give_by_owner, delete_give_by_owner

from datetime import datetime

# role creation confirmation
class RoleConfirmationView(View):
    def __init__(self, ctx, name, colour, settings_roles, settings_prices, timeout=60):
        super().__init__(timeout=timeout)
        self.ctx = ctx
        self.name = name
        self.colour = colour
        self.settings_roles = settings_roles
        self.settings_prices = settings_prices

    async def on_timeout(self):
        embed = set_invalid_time(self.ctx, 'Создание личной роли')
        await self.ctx.send(embed=embed, view=View())
    
    @button(label='Да', custom_id='btn_yes')
    async def button_callback_yes(self, button, interaction):
        if interaction.user.id == self.ctx.author.id:
            role = await self.ctx.guild.create_role(name=self.name)
            pos = self.ctx.guild.get_role(self.settings_roles.get('personal_role'))

            await role.edit(position=pos.position - 1, colour=self.colour)
            await self.ctx.author.add_roles(role)

            await add_role(self.ctx.author.id, role.id)
            await take_money(self.ctx.author.id, self.settings_prices.get('role_create'))

            logger.info(f'/create role - owner: {self.ctx.author.id} - role_id: {role.id}')
            # add new transaction
            await add_transaction(self.ctx.author.id, f'Создание роли {role.mention}', -self.settings_prices.get('role_create'), datetime.now())

            embed = set_create_role(self.ctx, role)
            self.stop()
            await interaction.response.edit_message(embed=embed, view=View())
    
    @button(label='Нет', custom_id='btn_no')
    async def button_callback_no(self, button, interaction):
        if interaction.user.id == self.ctx.author.id:
            self.stop()
            await interaction.message.delete()

# role manage
class RolesEdit(View): 
    def __init__(self, ctx, role, time_pay, shop_cost, shop_status, settings_roles, settings_prices, timeout=120): 
        super().__init__(timeout=timeout) 
        self.ctx = ctx 
        self.role = role
        self.time_pay = time_pay 
        self.shop_cost = shop_cost
        self.shop_status = shop_status
        self.settings_roles = settings_roles 
        self.settings_prices = settings_prices

        self.button_back = Button(label='Отмена', custom_id='btn_back', row=1)
        self.select_menu = StringSelect(
            placeholder = '🔎 Выберите действие',
            options = [
                SelectOption(label='Изменить название', value='change_name'),
                SelectOption(label='Изменить цвет', value='change_color'),
                SelectOption(label='Выдать роль', value='give_role'),
                SelectOption(label='Забрать роль', value='take_role'),
                SelectOption(label='Добавить в магазин', value='add_shop'),
                SelectOption(label='Изменить стоимость', value='change_cost'),
                SelectOption(label='Удалить из магазина', value='delete_from_shop'),
                SelectOption(label='Удалить роль', value='delete_role'),
            ]
        )
        self.select_menu.callback = self.select_menu_callback
        self.add_item(self.select_menu)

    async def on_timeout(self):
        return
    
    async def button_callback_back(self, interaction):
        if interaction.user.id == self.ctx.author.id:
            embed = set_edit_role(self.ctx, self.role, await get_give_by_owner(self.role.id), self.time_pay, self.settings_prices.get('role_create'), 
                                  self.shop_status, self.shop_cost)
            await interaction.response.edit_message(embed=embed, view=self)
            return

    async def button_callback_no_verify(self, interaction):
        if interaction.user.id == self.ctx.author.id:
            embed = set_edit_role(self.ctx, self.role, await get_give_by_owner(self.role.id), self.time_pay, self.settings_prices.get('role_create'), 
                                  self.shop_status, self.shop_cost)
            await interaction.response.edit_message(embed=embed, view=self)

    async def select_menu_callback(self, interaction):
        if interaction.user.id == self.ctx.author.id:
            if self.select_menu.values[0] == 'change_name':
                await self.change_name(interaction)
            elif self.select_menu.values[0] == 'change_color':
                await self.change_color(interaction)
            elif self.select_menu.values[0] == 'give_role':
                await self.give_role(interaction)
            elif self.select_menu.values[0] == 'take_role':
                await self.take_role(interaction)
            elif self.select_menu.values[0] == 'add_shop':
                await self.add_shop(interaction)
            elif self.select_menu.values[0] == 'change_cost':
                await self.change_cost(interaction)
            elif self.select_menu.values[0] == 'delete_from_shop':
                await self.delete_from_shop(interaction)
            elif self.select_menu.values[0] == 'delete_role':
                await self.delete_role(interaction)
    
    async def change_name(self, interaction):
        view = View()

        if interaction.user.id == self.ctx.author.id:
            if await get_balance(self.ctx.author.id) >= self.settings_prices.get('role_change_name'):
                pass
            else:
                embed = set_invalid_money(self.ctx, 'Изменение названия роли', await get_balance(self.ctx.author.id))
                await interaction.send(embed=embed, ephemeral=True, view=View())
                return
            
            self.button_back.callback = self.button_callback_back
            view.add_item(self.button_back)

            embed = set_change_name_role(self.ctx, self.role)
            await interaction.response.edit_message(embed=embed, view=view)
            await interaction.followup.send("Напишите новое название личной роли.", ephemeral=True, delete_after=10)
            
            try:
                def check(message):
                        return interaction.user == message.author
                message = await self.ctx.bot.wait_for('message', timeout=60.0, check=check)
            except asyncio.TimeoutError:
                embed = set_invalid_time(self.ctx, 'Изменение названия роли')
                await interaction.followup.send(embed=embed, view=View())
                return
            
            view_verify = View()

            button_yes_verify = Button(label='Да', custom_id='btn_yes_verify')
            button_no_verify = Button(label='Нет', custom_id='btn_no_verify')

            async def button_callback_yes_verify(interaction):
                if interaction.user.id == self.ctx.author.id:
                    if len(message.content) <= 100:
                        await take_money(self.ctx.author.id, self.settings_prices.get('role_change_name'))
                        await self.role.edit(name=f'{message.content}')

                        logger.info(f'/change name role - owner: {self.ctx.author.id} - role_id: {self.role.id} - new_name: {message.content}')
                        # add new transaction
                        await add_transaction(self.ctx.author.id, f'Изменение названия роли {self.role.mention} на {message.content}', 
                                                -self.settings_prices.get('role_change_name'), datetime.now())

                        embed = set_success_change_name_role(self.ctx, self.role)
                        await interaction.response.edit_message(embed=embed, view=View())
                    else:
                        embed = set_error_symbols_change_name(self.ctx)
                        await interaction.send(embed=embed, ephemeral=True, view=View())
            
            button_yes_verify.callback = button_callback_yes_verify
            button_no_verify.callback = self.button_callback_no_verify

            view_verify.add_item(button_yes_verify)
            view_verify.add_item(button_no_verify)

            try:
                if message:
                    await message.delete()
            except disnake.NotFound:
                logger.error('/role manage name - message not found')

            embed = set_confirmation_change_name_role(self.ctx, message.content, self.settings_prices.get('role_change_name'))
            await interaction.edit_original_response(embed=embed, view=view_verify)

    async def change_color(self, interaction):
        view = View()

        if interaction.user.id == self.ctx.author.id:
            if await get_balance(self.ctx.author.id) >= self.settings_prices.get('role_change_color'):
                pass
            else:
                embed = set_invalid_money(self.ctx, 'Изменение названия роли', await get_balance(self.ctx.author.id))
                await interaction.send(embed=embed, ephemeral=True, view=View())
                return

            self.button_back.callback = self.button_callback_back
            view.add_item(self.button_back)

            embed = set_change_color_role(self.ctx, self.role)
            await interaction.response.edit_message(embed=embed, view=view)
            await interaction.followup.send("Напишите новый цвет личной роли.", ephemeral=True, delete_after=10)

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
                    logger.error('/role manage color - non-convertible color')
                    return
                except disnake.NotFound:
                    logger.error('/role manage color - message not found')
                    return
            except asyncio.TimeoutError:
                embed = set_invalid_time(self.ctx, 'Изменение  цвета роли')
                await interaction.followup.send(embed=embed, view=View())
                return
            
            view_verify = View()

            button_yes_verify = Button(label='Да', custom_id='btn_yes_verify')
            button_no_verify = Button(label='Нет', custom_id='btn_no_verify')

            async def button_callback_yes_verify(interaction):
                if interaction.user.id == self.ctx.author.id:
                    await take_money(self.ctx.author.id, self.settings_prices.get('role_change_color'))
                    await self.role.edit(color=colour)

                    logger.info(f'/change color role - owner: {self.ctx.author.id} - role_id: {self.role.id} - new_color: {colour}')
                    # add new transaction
                    await add_transaction(self.ctx.author.id, f'Изменение цвета роли {self.role.mention} на {colour}', 
                                            -self.settings_prices.get('role_change_color'), datetime.now())
                    
                    embed = set_success_change_color_role(self.ctx, self.role)
                    await interaction.response.edit_message(embed=embed, view=View())
            
            button_yes_verify.callback = button_callback_yes_verify
            button_no_verify.callback = self.button_callback_no_verify

            view_verify.add_item(button_yes_verify)
            view_verify.add_item(button_no_verify)

            embed = set_confirmation_change_color_role(self.ctx, message.content, self.settings_prices.get('role_change_color'))
            await interaction.edit_original_response(embed=embed, view=view_verify)

    async def give_role(self, interaction):
        view = View()

        if interaction.user.id == self.ctx.author.id:
            self.button_back.callback = self.button_callback_back
            view.add_item(self.button_back)

            # select menu with users
            class SelectUsers(UserSelect):
                def __init__(self, ctx, role, button_callback_no_verify):
                    super().__init__(placeholder='Выберите пользователя')
                    self.ctx = ctx
                    self.role = role
                    self.button_callback_no_verify = button_callback_no_verify
            
                async def callback(self, interaction):
                        user_id = int(interaction.data['values'][0])
                        selected_user = self.ctx.guild.get_member(user_id)

                        if selected_user.bot:
                            embed = set_invalid_user(self.ctx, 'Выдача роли пользователю', 'бота')
                            await interaction.send(embed=embed, ephemeral=True, view=View())
                            return
                        elif selected_user is None:
                            embed = set_user_not_found(self.ctx, 'Выдача роль пользователю')
                            await interaction.send(embed=embed, ephemeral=True, view=View())
                            return
                        elif user_id == interaction.user.id:
                            embed = set_invalid_user(self.ctx, 'Выдача роли пользователю', 'себя')
                            await interaction.send(embed=embed, ephemeral=True, view=View())
                            return
                        elif role := interaction.user.get_role(self.role.id):
                            if selected_user.get_role(role.id):
                                embed = set_error_already_have_role(self.ctx)
                                await interaction.send(embed=embed, ephemeral=True, view=View())
                                return
                            else:
                                await view_verify(selected_user, interaction)

        users_with_role = await get_len_user_give_by_owner(self.role.id)
        if users_with_role >= 3:
            embed = set_not_give_user_role(self.ctx)
            await interaction.response.edit_message(embed=embed, view=view)
        else:
            view.add_item(SelectUsers(self.ctx, self.role, self.button_callback_no_verify))
            embed = set_give_user_role(self.ctx, self.role, users_with_role)
            await interaction.response.edit_message(embed=embed, view=view)

        async def view_verify(selected_user, interaction):
            view_verify = View()

            button_yes_verify = Button(label='Да', custom_id='btn_yes_verify')
            button_no_verify = Button(label='Нет', custom_id='btn_no_verify')

            async def button_callback_yes_verify(interaction):
                if interaction.user.id == self.ctx.author.id:
                    await add_give_by_owner(self.role.id, selected_user.id)
                    await selected_user.add_roles(self.role)
                    logger.info(f'/role manage give - owner: {self.ctx.author.id} - role_id: {self.role.id} - new_user: {selected_user.id}')
                    embed = set_success_give_role(self.ctx, self.role, selected_user)
                    await interaction.response.edit_message(embed=embed, view=View())

            button_yes_verify.callback = button_callback_yes_verify
            button_no_verify.callback = self.button_callback_no_verify

            view_verify.add_item(button_yes_verify)
            view_verify.add_item(button_no_verify)

            embed = set_confirmation_give_role(self.ctx, self.role, selected_user)
            await interaction.response.edit_message(embed=embed, view=view_verify)

    async def take_role(self, interaction):
        view = View()

        if interaction.user.id == self.ctx.author.id:
            self.button_back.callback = self.button_callback_back
            view.add_item(self.button_back)

            # select menu with users
            class SelectUsers(UserSelect):
                def __init__(self, ctx, role, button_callback_no_verify):
                    super().__init__(placeholder='Выберите пользователя')
                    self.ctx = ctx
                    self.role = role
                    self.button_callback_no_verify = button_callback_no_verify
            
                async def callback(self, interaction):
                        user_id = int(interaction.data['values'][0])
                        selected_user = self.ctx.guild.get_member(user_id)

                        if selected_user.bot:
                            embed = set_invalid_user(self.ctx, 'Забрать роль у пользователя', 'бота')
                            await interaction.send(embed=embed, ephemeral=True, view=View())
                            return
                        elif selected_user is None:
                            embed = set_user_not_found(self.ctx, 'Забрать роль у пользователя')
                            await interaction.send(embed=embed, ephemeral=True, view=View())
                            return
                        elif user_id == interaction.user.id:
                            embed = set_invalid_user(self.ctx, 'Забрать роль у пользователя', 'себя')
                            await interaction.send(embed=embed, ephemeral=True, view=View())
                            return
                        elif role := interaction.user.get_role(self.role.id):
                            if not selected_user.get_role(role.id):
                                embed = set_error_have_role(self.ctx)
                                await interaction.send(embed=embed, ephemeral=True, view=View())
                                return
                            else:
                                await view_verify(selected_user, interaction)
        
        user_with_role = await get_len_user_give_by_owner(self.role.id)
        if user_with_role == 0:
            embed = set_take_not_user_role(self.ctx, self.role)
            await interaction.response.edit_message(embed=embed, view=view)
        else:
            view.add_item(SelectUsers(self.ctx, self.role, self.button_callback_no_verify))
            embed = set_take_user_role(self.ctx, self.role)
            await interaction.response.edit_message(embed=embed, view=view)

        async def view_verify(selected_user, interaction):
            view_verify = View()

            button_yes_verify = Button(label='Да', custom_id='btn_yes_verify')
            button_no_verify = Button(label='Нет', custom_id='btn_no_verify')

            async def button_callback_yes_verify(interaction):
                if interaction.user.id == self.ctx.author.id:
                    await delete_give_by_owner(self.role.id, selected_user.id)
                    await selected_user.remove_roles(self.role)
                    logger.info(f'/role manage take - owner: {self.ctx.author.id} - role_id: {self.role.id} - user: {selected_user.id}')
                    embed = set_success_take_role(self.ctx, self.role, selected_user)
                    await interaction.response.edit_message(embed=embed, view=View())

            button_yes_verify.callback = button_callback_yes_verify
            button_no_verify.callback = self.button_callback_no_verify

            view_verify.add_item(button_yes_verify)
            view_verify.add_item(button_no_verify)

            embed = set_confirmation_take_role(self.ctx, self.role, selected_user)
            await interaction.response.edit_message(embed=embed, view=view_verify)
    
    async def add_shop(self, interaction):
        view = View()

        if interaction.user.id == self.ctx.author.id:
            self.button_back.callback = self.button_callback_back
            view.add_item(self.button_back)

            if await is_exists_role_in_shop(self.role.id):
                embed = set_role_already_in_shop(self.ctx, self.role)
                await interaction.response.edit_message(embed=embed, view=view)
            else:
                embed = set_add_role_to_shop(self.ctx, self.role)
                await interaction.response.edit_message(embed=embed, view=view)
                await interaction.followup.send("Напишите стоимость Вашей роли для магазина.", ephemeral=True, delete_after=10)
        
            try: 
                def check(message):
                    return interaction.user == message.author and message.content.isdigit()
                message = await self.ctx.bot.wait_for('message', timeout=60.0, check=check)
                if not 500 <= int(message.content) <= 3000:
                    await message.delete()
                    embed = set_invalid_cost_role(self.ctx, 'Добавление роли в магазин')
                    await interaction.followup.send(embed=embed, ephemeral=True, view=View())
                    return
            except asyncio.TimeoutError:
                embed = set_invalid_time(self.ctx, 'Добавление роли в магазин')
                await interaction.followup.send(embed=embed, view=View())
                return
            
            view_verify = View()

            button_yes_verify = Button(label='Да', custom_id='btn_yes_verify')
            button_no_verify = Button(label='Нет', custom_id='btn_no_verify')

            async def button_callback_yes_verify(interaction):
                if interaction.user.id == self.ctx.author.id:
                    await add_role_to_shop(self.role.id, message.content)
                    logger.info(f'/add role to shop - owner: {self.ctx.author.id} - role_id: {self.role.id} - cost: {message.content}')

                    embed = set_success_add_role_to_shop(self.ctx, self.role, message.content)
                    await interaction.response.edit_message(embed=embed, view=View())
            
            button_yes_verify.callback = button_callback_yes_verify
            button_no_verify.callback = self.button_callback_no_verify

            view_verify.add_item(button_yes_verify)
            view_verify.add_item(button_no_verify)

            try:
                if message:
                    await message.delete()
            except disnake.NotFound:
                logger.error('/role manage add to shop - message not found')
                return
                
            embed = set_confirmation_add_role_to_shop(self.ctx, self.role, message.content)
            await interaction.edit_original_response(embed=embed, view=view_verify)
    
    async def change_cost(self, interaction):
        view = View()

        if interaction.user.id == self.ctx.author.id:
            self.button_back.callback = self.button_callback_back
            view.add_item(self.button_back)

            if await is_exists_role_in_shop(self.role.id):
                embed = set_change_cost_role(self.ctx, self.role)
                await interaction.response.edit_message(embed=embed, view=view)
                await interaction.followup.send("Напишите новую стоимость Вашей роли для магазина.", ephemeral=True, delete_after=10)
            else:
                embed = set_invalid_role_shop(self.ctx, 'Изменение стоимости роли в магазине')
                await interaction.response.edit_message(embed=embed, view=view)
                return

            try: 
                def check(message): 
                    return interaction.user == message.author and message.content.isdigit()
                message = await self.ctx.bot.wait_for('message', timeout=60.0, check=check)
                if not 500 <= int(message.content) <= 3000:
                    await message.delete()
                    embed = set_invalid_cost_role(self.ctx, 'Изменение стоимости роли в магазине')
                    await interaction.followup.send(embed=embed, ephemeral=True, view=View())
                    return
            except asyncio.TimeoutError:
                embed = set_invalid_time(self.ctx, 'Изменение стоимости роли в магазине')
                await interaction.followup.send(embed=embed, view=View())
                return
            
            view_verify = View()

            button_yes_verify = Button(label='Да', custom_id='btn_yes_verify')
            button_no_verify = Button(label='Нет', custom_id='btn_no_verify')

            async def button_callback_yes_verify(interaction):
                if interaction.user.id == self.ctx.author.id:
                    await change_cost_role_in_shop(self.role.id, message.content)
                    logger.info(f'/change cost role to shop - owner: {self.ctx.author.id} - role_id: {self.role.id} - new_cost: {message.content}')

                    embed = set_success_change_cost_role(self.ctx, self.role, message.content)
                    await interaction.response.edit_message(embed=embed, view=View())
            
            button_yes_verify.callback = button_callback_yes_verify
            button_no_verify.callback = self.button_callback_no_verify

            view_verify.add_item(button_yes_verify)
            view_verify.add_item(button_no_verify)

            try:
                if message:
                    await message.delete()
            except disnake.NotFound:
                logger.error('/role manage change cost - message not found')
                return
                
            embed = set_confirmation_change_cost_role(self.ctx, self.role, message.content)
            await interaction.edit_original_response(embed=embed, view=view_verify)
    
    async def delete_from_shop(self, interaction):
        if interaction.user.id == self.ctx.author.id:
            if await is_exists_role_in_shop(self.role.id):
                view_verify = View()

                button_yes_verify = Button(label='Да', custom_id='btn_yes_verify')
                button_no_verify = Button(label='Нет', custom_id='btn_no_verify')

                async def button_callback_yes_verify(interaction):
                    if interaction.user.id == self.ctx.author.id:
                        await delete_role_from_shop(self.role.id)
                        logger.info(f'/delete role from shop - owner: {self.ctx.author.id} - role_id: {self.role.id}')

                        embed = set_success_delete_role_from_shop(self.ctx)
                        await interaction.response.edit_message(embed=embed, view=View())
                
                button_yes_verify.callback = button_callback_yes_verify
                button_no_verify.callback = self.button_callback_no_verify

                view_verify.add_item(button_yes_verify)
                view_verify.add_item(button_no_verify)

                embed = set_confirmation_delete_role_from_shop(self.ctx, self.role)
                await interaction.response.edit_message(embed=embed, view=view_verify)
            else:
                view = View()
                self.button_back.callback = self.button_callback_back
                view.add_item(self.button_back)

                embed = set_invalid_role_shop(self.ctx, 'Удаление роли из магазина')
                await interaction.response.edit_message(embed=embed, view=view)
                return

    async def delete_role(self, interaction):
        if interaction.user.id == self.ctx.author.id:
            view_verify = View()

            button_yes_verify = Button(label='Да', custom_id='btn_yes_verify')
            button_no_verify = Button(label='Нет', custom_id='btn_no_verify')

            async def button_callback_yes_verify(interaction):
                if interaction.user.id == self.ctx.author.id:
                    await delete_role(self.role.id)
                    await self.role.delete()
                    logger.info(f'/delete role - owner: {self.ctx.author.id} - role_id: {self.role.id}')

                    embed = set_success_delete_role(self.ctx)
                    await interaction.response.edit_message(embed=embed, view=View())

            button_yes_verify.callback = button_callback_yes_verify
            button_no_verify.callback = self.button_callback_no_verify

            view_verify.add_item(button_yes_verify)
            view_verify.add_item(button_no_verify)

            embed = set_confirmation_delete_role(self.ctx, self.role)
            await interaction.response.edit_message(embed=embed, view=view_verify)