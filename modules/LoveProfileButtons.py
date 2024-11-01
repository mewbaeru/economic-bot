from disnake import ButtonStyle
from disnake.ui import View, button, Button

from modules.Logger import *
from modules.Embeds import *
from database.requests import write_data_love_room, get_balance, take_money, add_transaction, get_info_marriage, update_love_room_balance, divorce_marriage

class LoveProfileView(View):
    def __init__(self, ctx, member, marriage_data, love_room_data, settings_roles, timeout=60):
        super().__init__(timeout=timeout)
        self.ctx = ctx
        self.member = member
        self.marriage_data = marriage_data
        self.settings_roles = settings_roles
        self.love_room_data = love_room_data
    
    @button(label='Изменить название', custom_id='btn_change_name')
    async def button_callback_change_name(self, button, interaction):
        if self.ctx.author.id == interaction.user.id:
            class ChangeNameModal(disnake.ui.Modal):
                def __init__(self, ctx, member, marriage_data, love_room_data):
                    self.ctx = ctx
                    self.member = member
                    self.marriage_data = marriage_data
                    self.love_room_data = love_room_data

                    components = [
                        disnake.ui.TextInput(label=f'Введите новое название', 
                                             placeholder='Например: mewbaeru', min_length=1, max_length=100, custom_id='name_love_room_input')
                    ]
                    super().__init__(title=f'Изменение названия любовной комнаты', custom_id='name_love_room_input', components=components)

                async def callback(self, interaction):
                    name_love_room = str(interaction.text_values['name_love_room_input'])
                    await write_data_love_room(self.member.id, 'name', f'{name_love_room}')

                    logger.info(f"/change name love room - partner: {self.member.id} - new_name: {name_love_room}")

                    embed = set_cuccess_change_name_love_room(self.ctx, name_love_room)
                    await interaction.response.send_message(embed=embed, ephemeral=True)
                
            await interaction.response.send_modal(ChangeNameModal(self.ctx, self.member, self.marriage_data, self.love_room_data))

    @button(label='Пополнить баланс', custom_id='btn_update_balance', style=ButtonStyle.primary)
    async def button_callback_change_balance(self, button, interaction):
        if self.ctx.author.id == interaction.user.id:
            class ToppingUpBalanceModal(disnake.ui.Modal):
                def __init__(self, ctx, member, marriage_data, love_room_data):
                    self.ctx = ctx
                    self.member = member
                    self.marriage_data = marriage_data
                    self.love_room_data = love_room_data

                    components = [
                        disnake.ui.TextInput(label=f'Введите сумму', 
                                             placeholder='Например: 1000', min_length=1, max_length=10, custom_id='topping_up_love_room_input')
                    ]
                    super().__init__(title=f'Пополнение любовной комнаты', custom_id='topping_up_love_room_input', components=components)

                async def callback(self, interaction):
                    amount = int(interaction.text_values['topping_up_love_room_input'])

                    if amount <= await get_balance(self.member.id):
                        await take_money(self.member.id, amount)
                        await update_love_room_balance(self.member.id, amount)

                        logger.info(f"/topping up love room balance - partner: {self.member.id} - amount: {amount}")
                        # add new transaction
                        await add_transaction(self.member.id, f'Пополнение любовной комнаты', -amount, datetime.now())

                        marriage_data = await get_info_marriage(self.member.id)

                        new_balance = marriage_data[2]

                        embed = set_cuccess_update_balance_love_room(self.ctx, amount, new_balance)
                        await interaction.response.send_message(embed=embed, ephemeral=True)
                    else:
                        embed = set_invalid_money(self.ctx, 'Пополнение любовной комнаты', await get_balance(self.member.id))
                        await interaction.response.send_message(embed=embed, ephemeral=True)
                    
            await interaction.response.send_modal(ToppingUpBalanceModal(self.ctx, self.member, self.marriage_data, self.love_room_data))           

    @button(label='Развестись', custom_id='btn_divorse_marriage', style=ButtonStyle.red)
    async def button_callback_divorce_marriage(self, button, interaction):
        if self.ctx.author.id == interaction.user.id:
            view_verify = View()

            button_yes_verify = Button(emoji='<:gray_check_mark_mewbae:1276606963203047555>', custom_id='btn_yes_verify')
            button_no_verify = Button(emoji='<:gray_negative_squared_cross_mark:1276606994752737433>', custom_id='btn_no_verify')

            async def button_callback_yes_verify(interaction):
                if interaction.user.id == self.ctx.author.id:
                    view = View()

                    role_marry = self.settings_roles.get('marry_role')
                    role = disnake.utils.get(self.ctx.guild.roles, id=role_marry)
                    partner_1_id = self.marriage_data[0]
                    partner_2_id = self.marriage_data[1]
                    partner_1_member = self.ctx.guild.get_member(partner_1_id)
                    partner_2_member = self.ctx.guild.get_member(partner_2_id)
                    await partner_1_member.remove_roles(role)
                    await partner_2_member.remove_roles(role)

                    await divorce_marriage(self.member.id)

                    logger.info(f'/divorce marriage - partner: {self.member.id}')

                    embed = set_success_divorce_marriage(self.ctx)
                    await interaction.response.edit_message(embed=embed, view=view)
            
            async def button_callback_no_verify(interaction):
                if interaction.user.id == self.ctx.author.id:
                    await interaction.message.delete()

            button_yes_verify.callback = button_callback_yes_verify
            button_no_verify.callback = button_callback_no_verify

            view_verify.add_item(button_yes_verify)
            view_verify.add_item(button_no_verify)

            embed = set_confirmation_divorce_marriage(self.ctx)
            await interaction.response.send_message(embed=embed, view=view_verify)

    async def on_timeout(self):
        return