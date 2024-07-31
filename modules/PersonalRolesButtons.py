import asyncio
from disnake import MessageInteraction
from disnake.ui import View, button, Button, UserSelect

from modules.Logger import *
from modules.Embeds import *
from database.requests import add_role, take_money, get_balance, delete_role

from datetime import datetime, timedelta

# role creation confirmation
class RoleConfirmationView(View):
    def __init__(self, ctx, name, colour, settings_roles, cost_role_create, timeout=120):
        super().__init__(timeout=timeout)
        self.ctx = ctx
        self.name = name
        self.colour = colour
        self.settings_roles = settings_roles
        self.cost_role_create = cost_role_create

    async def on_timeout(self):
        embed = set_timeout(self.ctx)
        await self.ctx.send(embed=embed, view=View())
    
    @button(label='Да', custom_id='btn_yes')
    async def button_callback_yes(self, button, interaction):
        if interaction.user.id == self.ctx.author.id:
            role = await self.ctx.guild.create_role(name=self.name)
            pos = self.ctx.guild.get_role(self.settings_roles.get('personal_role'))

            await role.edit(position=pos.position - 1, colour=self.colour)
            await self.ctx.author.add_roles(role)

            await add_role(self.ctx.author.id, role.id)
            await take_money(self.ctx.author.id, self.cost_role_create)
            logger.info(f'/create role - owner: {self.ctx.author.id} - role_id: {role.id}')

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
    def __init__(self, ctx, role, time_pay, cost_role_create, cost_role_change_name, cost_role_change_color, timeout=120):
        super().__init__(timeout=timeout)
        self.ctx = ctx
        self.role = role
        self.time_pay = time_pay
        self.cost_role_create = cost_role_create
        self.cost_role_change_name = cost_role_change_name
        self.cost_role_change_color = cost_role_change_color
        self.button_back = Button(label='Отмена', custom_id='btn_back')
    
    async def button_callback_back(self, interaction):
                if interaction.user.id == self.ctx.author.id:
                    embed = set_edit_role(self.ctx, self.role, self.time_pay, self.cost_role_create)
                    await interaction.response.edit_message(embed=embed, view=RolesEdit(self.ctx, self.role, self.time_pay, self.cost_role_create, 
                                                                                        self.cost_role_change_name, self.cost_role_change_color))
                    return
    
    async def button_callback_no_verify(self, interaction):
                            if interaction.user.id == self.ctx.author.id:
                                embed = set_edit_role(self.ctx, self.role, self.time_pay, self.cost_role_create)
                                await interaction.response.edit_message(embed=embed, view=RolesEdit(self.ctx, self.role, self.time_pay, self.cost_role_create,
                                                                                    self.cost_role_change_name, self.cost_role_change_color))

    @button(label='Изменить название', custom_id='btn_change_name')
    async def button_change_name(self, button, interaction):
        view = View()

        if interaction.user.id == self.ctx.author.id:
            self.button_back.callback = self.button_callback_back
            view.add_item(self.button_back)

            embed = set_change_name_role(self.ctx, self.role)
            await interaction.response.edit_message(embed=embed, view=view)
            await interaction.followup.send("Напишите новое название личной роли.", ephemeral=True, delete_after=30)

            try:
                def check(message):
                        return interaction.user == message.author
                message = await self.ctx.bot.wait_for('message', timeout=30.0, check=check)
            except asyncio.TimeoutError:
                embed = set_invalid_change_role(self.ctx)
                await interaction.followup.send(embed=embed, view=View())
                return
            
            view_verify = View()

            button_yes_verify = Button(label='Да', custom_id='btn_yes_verify')
            button_no_verify = Button(label='Нет', custom_id='btn_no_verify')

            async def button_callback_yes_verify(interaction):
                if interaction.user.id == self.ctx.author.id:
                    if await get_balance(self.ctx.author.id) >= self.cost_role_change_name:
                        if len(message.content) <= 100:
                            await take_money(self.ctx.author.id, self.cost_role_change_name)
                            await self.role.edit(name=f'{message.content}')

                            embed = set_success_change_name_role(self.ctx, self.role)
                            await interaction.response.edit_message(embed=embed, view=View())
                        else:
                            embed = set_error_symbols_change_name_role(self.ctx, self.role)
                            await interaction.send(embed=embed, ephemeral=True, view=View())
                    else:
                        embed = set_error_change_role(self.ctx, self.role)
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

            embed = set_confirmation_change_name_role(self.ctx, message.content, self.cost_role_change_name)
            await interaction.edit_original_response(embed=embed, view=view_verify)
    
    @button(label='Изменить цвет', custom_id='btn_change_color')
    async def button_change_color(self, button, interaction):
        view = View()

        if interaction.user.id == self.ctx.author.id:
            self.button_back.callback = self.button_callback_back
            view.add_item(self.button_back)

            embed = set_change_color_role(self.ctx, self.role)
            await interaction.response.edit_message(embed=embed, view=view)
            await interaction.followup.send("Напишите новый цвет личной роли.", ephemeral=True, delete_after=30)

            try:
                def check(message):
                    return interaction.user == message.author
                message = await self.ctx.bot.wait_for('message', timeout=30.0, check=check)
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
                embed = set_invalid_change_role(self.ctx)
                await interaction.followup.send(embed=embed, view=View())
                return
            
            view_verify = View()

            button_yes_verify = Button(label='Да', custom_id='btn_yes_verify')
            button_no_verify = Button(label='Нет', custom_id='btn_no_verify')

            async def button_callback_yes_verify(interaction):
                if interaction.user.id == self.ctx.author.id:
                    if await get_balance(self.ctx.author.id) >= self.cost_role_change_color:
                        await take_money(self.ctx.author.id, self.cost_role_change_color)
                        await self.role.edit(color=colour)

                        embed = set_success_change_color_role(self.ctx, self.role)
                        await interaction.response.edit_message(embed=embed, view=View())
                    else:
                        embed = set_error_change_role(self.ctx, self.role)
                        await interaction.send(embed=embed, ephemeral=True, view=View())
            
            button_yes_verify.callback = button_callback_yes_verify
            button_no_verify.callback = self.button_callback_no_verify

            view_verify.add_item(button_yes_verify)
            view_verify.add_item(button_no_verify)

            embed = set_confirmation_change_color_role(self.ctx, message.content, self.cost_role_change_color)
            await interaction.edit_original_response(embed=embed, view=view_verify)
    
    @button(label='Выдать роль', custom_id='btn_give_role')
    async def button_give_role(self, button, interaction):
        view = View()

        if interaction.user.id == self.ctx.author.id:
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
                            embed = set_error_bot_give_role(self.ctx)
                            await interaction.send(embed=embed, ephemeral=True, view=View())
                            return
                        elif selected_user is None:
                            embed = set_error_not_user_give_role(self.ctx)
                            await interaction.send(embed=embed, ephemeral=True, view=View())
                            return
                        elif user_id == interaction.user.id:
                            embed = set_error_give_yourself_role(self.ctx)
                            await interaction.send(embed=embed, ephemeral=True, view=View())
                            return
                        elif role := interaction.user.get_role(self.role.id):
                            if selected_user.get_role(role.id):
                                embed = set_error_already_have_role(self.ctx)
                                await interaction.send(embed=embed, ephemeral=True, view=View())
                                return
                            else:
                                await view_verify(selected_user, interaction)
            
        view.add_item(SelectUsers(self.ctx, self.role, self.button_callback_no_verify))
        embed = set_give_user_role(self.ctx, self.role)
        await interaction.response.edit_message(embed=embed, view=view)

        async def view_verify(selected_user, interaction):
            view_verify = View()

            button_yes_verify = Button(label='Да', custom_id='btn_yes_verify')
            button_no_verify = Button(label='Нет', custom_id='btn_no_verify')

            async def button_callback_yes_verify(interaction):
                if interaction.user.id == self.ctx.author.id:
                    await selected_user.add_roles(self.role)
                    embed = set_success_give_role(self.ctx, self.role, selected_user)
                    await interaction.response.edit_message(embed=embed, view=View())

            button_yes_verify.callback = button_callback_yes_verify
            button_no_verify.callback = self.button_callback_no_verify

            view_verify.add_item(button_yes_verify)
            view_verify.add_item(button_no_verify)

            embed = set_confiramtion_give_role(self.ctx, self.role, selected_user)
            await interaction.response.edit_message(embed=embed, view=view_verify)
    
    @button(label='Забрать роль', custom_id='btn_take_role')
    async def button_take_role(self, button, interaction):
        view = View()

        if interaction.user.id == self.ctx.author.id:
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
                            embed = set_error_bot_take_role(self.ctx)
                            await interaction.send(embed=embed, ephemeral=True, view=View())
                            return
                        elif selected_user is None:
                            embed = set_error_not_user_take_role(self.ctx)
                            await interaction.send(embed=embed, ephemeral=True, view=View())
                            return
                        elif user_id == interaction.user.id:
                            embed = set_error_take_yourself_role(self.ctx)
                            await interaction.send(embed=embed, ephemeral=True, view=View())
                            return
                        elif role := interaction.user.get_role(self.role.id):
                            if not selected_user.get_role(role.id):
                                embed = set_error_have_role(self.ctx)
                                await interaction.send(embed=embed, ephemeral=True, view=View())
                                return
                            else:
                                await view_verify(selected_user, interaction)
        
        user_with_role = len([member for member in self.ctx.guild.members if member != self.ctx.author and self.role in member.roles])
        if not user_with_role:
            embed = set_take_not_user_role(self.ctx, self.role)
            await interaction.send(embed=embed, ephemeral=True, view=View())
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
                    await selected_user.remove_roles(self.role)
                    embed = set_success_take_role(self.ctx, self.role, selected_user)
                    await interaction.response.edit_message(embed=embed, view=View())

            button_yes_verify.callback = button_callback_yes_verify
            button_no_verify.callback = self.button_callback_no_verify

            view_verify.add_item(button_yes_verify)
            view_verify.add_item(button_no_verify)

            embed = set_confiramtion_take_role(self.ctx, self.role, selected_user)
            await interaction.response.edit_message(embed=embed, view=view_verify)
    
    @button(label='Удалить роль', custom_id='delete_role')
    async def delete_role(self, button, interaction):
        if interaction.user.id == self.ctx.author.id:
            view_verify = View()

            button_yes_verify = Button(label='Да', custom_id='btn_yes_verify')
            button_no_verify = Button(label='Нет', custom_id='btn_no_verify')

            async def button_callback_yes_verify(interaction):
                if interaction.user.id == self.ctx.author.id:
                    await delete_role(self.ctx.author.id)
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