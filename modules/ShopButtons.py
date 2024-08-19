from disnake import SelectOption
from disnake.ui import View, button, Button, StringSelect

from modules.Logger import *
from modules.Embeds import *
from database.requests import get_balance, get_cost_role_in_shop, take_money, add_count_user, give_money, add_transaction

from datetime import datetime

# shop
class ShopView(View):
    def __init__(self, ctx, page, roles, total_pages, settings_roles, settings_prices , timeout=60):
        super().__init__(timeout=timeout)
        self.ctx = ctx
        self.page = page
        self.roles = roles
        self.total_pages = total_pages
        self.settings_roles = settings_roles
        self.settings_prices = settings_prices

        # add buttons for buy roles
        self.page_roles = roles[(page-1)*5:page*5]
        self.buy_buttons = []
        self.role_owners = {}
        self.role_prices = {}

        for i, (role_id, time, owner_id, price, count) in enumerate(self.page_roles):
            self.buy_buttons.append(Button(label=f'{(self.page-1)*5+i+1}', custom_id=f'buy_role_{role_id}', row=0))

            self.role_owners[role_id] = owner_id
            self.role_prices[role_id] = price
            
            self.buy_buttons[i].callback = self.button_callback_buy_role
            self.add_item(self.buy_buttons[i])

        # add select menu for sorting roles
        self.sorting_select_menu = StringSelect(
            placeholder = '🔎 Сортировать роли',
            options = [
                SelectOption(label='Сначала новые', value='new_roles'),
                SelectOption(label='Сначала старые', value='old_roles'),
                # not done
                SelectOption(label='Сначала дешевые', value='cheap_roles'),
                SelectOption(label='Сначала дорогие', value='rich_roles'),
                SelectOption(label='Сначала популярные', value='popular_roles'),
                SelectOption(label='Сначала непопулярные', value='unpopular_roles'),
            ]
        )
        self.sorting_select_menu.callback = self.sorting_select_menu_callback
        self.add_item(self.sorting_select_menu)

        # add select menu for choose shop
        self.choose_shop_select_menu = StringSelect(
            placeholder = '🔎 Выбор магазина',
            options = [
                SelectOption(label='Магазин ролей', value='roles_shop'),
                SelectOption(label='Магазин прочего', value='another_shop'),
            ]
        )
        self.choose_shop_select_menu.callback = self.choose_shop_select_menu_callback
        self.add_item(self.choose_shop_select_menu)

    async def on_timeout(self):
        return
    
    # set embed with roles shop
    async def update_embed(self, interaction):
        self.page = max(min(self.page, self.total_pages), 1)
        embed = set_shop(self.ctx, self.roles, self.page, self.total_pages)
        await interaction.response.edit_message(embed=embed, view=ShopView(self.ctx, self.page, self.roles, self.total_pages, self.settings_roles.get('role_of_sending_images'), 
                                                                           self.settings_prices.get('add_role_of_sending_images')))
    
    # set embed with another shop
    async def another_shop(self, interaction):
        view = View()

        self.page = max(min(self.page, self.total_pages), 1)
        buy_button = Button(label='1', custom_id='buy_additional_role')
        buy_button.callback = self.button_callback_buy_additional_role
        view.add_item(buy_button)
        view.add_item(self.choose_shop_select_menu)

        embed = set_another_shop(self.ctx, 1500, self.page, self.total_pages)
        await interaction.response.edit_message(embed=embed, view=view)

    async def button_callback_buy_role(self, interaction):
        if interaction.user.id == self.ctx.author.id:
            role_id = int(interaction.data['custom_id'].split('_')[-1])
            role = disnake.utils.get(self.ctx.guild.roles, id=role_id)

            # exception
            if role in self.ctx.author.roles:
                embed = set_already_have_role(self.ctx)
                await interaction.send(embed=embed, ephemeral=True, view=View())
                return
            
            if await get_balance(self.ctx.author.id) >= await get_cost_role_in_shop(role_id):
                pass
            else:
                await give_money(self.ctx.author.id, 100000)
                embed = set_invalid_money(self.ctx, 'Приобретение роли', await get_balance(self.ctx.author.id))
                await interaction.send(embed=embed, ephemeral=True, view=View())
                return
            
            view_verify = View()

            button_yes_verify = Button(label='Да', custom_id='btn_yes_verify')
            button_no_verify = Button(label='Нет', custom_id='btn_no_verify')

            async def button_callback_yes_verify(interaction):
                if interaction.user.id == self.ctx.author.id:
                    await add_count_user(role_id)
                    await take_money(self.ctx.author.id, await get_cost_role_in_shop(role_id))
                    await give_money(self.role_owners[role_id], self.role_prices[role_id])
                    await interaction.user.add_roles(role)

                    logger.info(f'/shop - role_id: {role_id} - buyer: {self.ctx.author.id}')
                    # add new transaction
                    await add_transaction(self.ctx.author.id, f'Приобретение роли {role.mention}', 
                                            -self.role_prices[role_id], datetime.now())
                    
                    embed = set_success_buy_role(self.ctx, role, await get_cost_role_in_shop(role_id))
                    await interaction.response.edit_message(embed=embed, view=View())

            async def button_callback_no_verify(interaction):
                if interaction.user.id == self.ctx.author.id:
                    embed = set_shop(self.ctx, self.roles, self.page, self.total_pages)
                    await interaction.response.edit_message(embed=embed, view=self)

            button_yes_verify.callback = button_callback_yes_verify
            button_no_verify.callback = button_callback_no_verify

            view_verify.add_item(button_yes_verify)
            view_verify.add_item(button_no_verify)

            embed = set_confirmation_buy_role(self.ctx, role, await get_cost_role_in_shop(role_id))
            await interaction.response.edit_message(embed=embed, view=view_verify)
    
    async def button_callback_buy_additional_role(self, interaction):
        if interaction.user.id == self.ctx.author.id:
            additional_role = disnake.utils.get(self.ctx.guild.roles, id=self.settings_roles.get('role_of_sending_images'))

            # exception
            if additional_role in self.ctx.author.roles:
                embed = set_already_have_role(self.ctx)
                await interaction.send(embed=embed, ephemeral=True, view=View())
                return
            if await get_balance(self.ctx.author.id) >= self.settings_prices.get('add_role_of_sending_images'):
                pass
            else:
                embed = set_invalid_money(self.ctx, 'Приобретение роли', await get_balance(self.ctx.author.id))
                await interaction.send(embed=embed, ephemeral=True, view=View())
                return

            view_verify = View()

            button_yes_verify = Button(label='Да', custom_id='btn_yes_verify')
            button_no_verify = Button(label='Нет', custom_id='btn_no_verify')

            async def button_callback_yes_verify(interaction):
                if interaction.user.id == self.ctx.author.id:
                    await take_money(self.ctx.author.id, self.settings_prices.get('add_role_of_sending_images'))
                    additional_role = disnake.utils.get(self.ctx.guild.roles, id=self.settings_roles.get('role_of_sending_images'))
                    await interaction.user.add_roles(additional_role)

                    logger.info(f'/shop - role_id: {additional_role.id} - buyer: {self.ctx.author.id}')
                    # add new transaction
                    await add_transaction(self.ctx.author.id, f'Приобретение роли {additional_role.mention}', 
                                            -self.settings_prices.get('add_role_of_sending_images'), datetime.now())
                    
                    embed = set_success_buy_additional_role(self.ctx, self.settings_roles.get('role_of_sending_images'), 
                                                            self.settings_prices.get('add_role_of_sending_images'))
                    await interaction.response.edit_message(embed=embed, view=View())
            
            async def button_callback_no_verify(interaction):
                if interaction.user.id == self.ctx.author.id:
                    embed = set_another_shop(self.ctx, self.settings_prices.get('add_role_of_sending_images'), self.page, self.total_pages)
                    await interaction.response.edit_message(embed=embed, view=self)
            
            button_yes_verify.callback = button_callback_yes_verify
            button_no_verify.callback = button_callback_no_verify

            view_verify.add_item(button_yes_verify)
            view_verify.add_item(button_no_verify)

            embed = set_confirmation_buy_additional_role(self.ctx, self.settings_roles.get('role_of_sending_images'), 
                                                         self.settings_prices.get('add_role_of_sending_images'))
            await interaction.response.edit_message(embed=embed, view=view_verify)
            
    async def sorting_select_menu_callback(self, interaction):
        if interaction.user.id == self.ctx.author.id:
            if self.sorting_select_menu.values[0] == 'new_roles':
                await self.new_roles(interaction)
            elif self.sorting_select_menu.values[0] == 'old_roles':
                await self.old_roles(interaction)
            elif self.sorting_select_menu.values[0] == 'cheap_roles':
                await self.cheap_roles(interaction)
            elif self.sorting_select_menu.values[0] == 'rich_roles':
                await self.rich_roles(interaction)
            elif self.sorting_select_menu.values[0] == 'popular_roles':
                await self.popular_roles(interaction)
            elif self.sorting_select_menu.values[0] == 'unpopular_roles':
                await self.unpopular_roles(interaction)
    
    async def choose_shop_select_menu_callback(self, interaction):
        if interaction.user.id == self.ctx.author.id:
            if self.choose_shop_select_menu.values[0] == 'roles_shop':
                await self.update_embed(interaction)
            elif self.choose_shop_select_menu.values[0] == 'another_shop':
                await self.another_shop(interaction)

    async def new_roles(self, interaction):
        self.roles.sort(key=lambda x: x[1], reverse=True) 
        self.page_roles = self.roles[(self.page-1)*5:self.page*5]
        await self.update_embed(interaction)
    
    async def old_roles(self, interaction):
        self.roles.sort(key=lambda x: x[1], reverse=False) 
        self.page_roles = self.roles[(self.page-1)*5:self.page*5]
        await self.update_embed(interaction)
    
    async def cheap_roles(self, interaction):
        self.roles.sort(key=lambda x: x[3], reverse=False) 
        self.page_roles = self.roles[(self.page-1)*5:self.page*5]
        await self.update_embed(interaction)
    
    async def rich_roles(self, interaction):
        self.roles.sort(key=lambda x: x[3], reverse=True) 
        self.page_roles = self.roles[(self.page-1)*5:self.page*5]
        await self.update_embed(interaction)
    
    async def popular_roles(self, interaction):
        self.roles.sort(key=lambda x: x[4], reverse=True) 
        self.page_roles = self.roles[(self.page-1)*5:self.page*5]
        await self.update_embed(interaction)

    async def unpopular_roles(self, interaction):
        self.roles.sort(key=lambda x: x[4], reverse=False) 
        self.page_roles = self.roles[(self.page-1)*5:self.page*5]
        await self.update_embed(interaction)
        
    @button(label='⋘', custom_id='first_page_shop', row=3)
    async def button_first_page_shop(self, button, interaction):
        if interaction.user.id == self.ctx.author.id:
            self.page = 1
            await self.update_embed(interaction)

    @button(label='≪', custom_id='back_page_shop', row=3)
    async def button_back_page_shop(self, button, interaction):
        if interaction.user.id == self.ctx.author.id:
            self.page -= 1
            await self.update_embed(interaction)
    
    @button(label='🗑️', custom_id='delete_shop', row=3)
    async def buttin_delete_shop(self, button, interaction):
        if interaction.user.id == self.ctx.author.id:
            await interaction.message.delete()

    @button(label='≫', custom_id='next_page_shop', row=3)
    async def button_next_page_shop(self, button, interaction):
        if interaction.user.id == self.ctx.author.id:
            self.page += 1
            await self.update_embed(interaction)
    
    @button(label='⋙', custom_id='last_page_shop', row=3)
    async def button_last_page_shop(self, button, interaction):
        if interaction.user.id == self.ctx.author.id:
            self.page = self.total_pages
            await self.update_embed(interaction)