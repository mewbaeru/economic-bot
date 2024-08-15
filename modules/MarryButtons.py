from disnake.ui import View, button

from modules.Logger import *
from modules.Embeds import *
from database.requests import take_money, update_marry, add_transaction

import random
from datetime import datetime

# coinflip
class MarryView(View):
    def __init__(self, ctx, member, role_marry, cost_marry, timeout=60):
        super().__init__(timeout=timeout)
        self.ctx = ctx
        self.member= member
        self.role_marry = role_marry
        self.cost_marry = cost_marry
    
    @button(label='Да', custom_id='btn_yes')
    async def button_callback_yes(self, button, interaction):
        if interaction.user == self.member:
            await take_money(self.ctx.author.id, self.cost_marry)
            await update_marry(self.ctx.author.id)
            await update_marry(self.member.id)

            role = disnake.utils.get(self.ctx.guild.roles, id=self.role_marry)
            await self.ctx.author.add_roles(role)
            await self.member.add_roles(role)

            logger.info(f"/marry - member: {self.ctx.author.id} - member: {self.member.id}")
            # add new transaction
            await add_transaction(self.ctx.author.id, f'Заключение брака с {self.member.mention}', -self.cost_marry, datetime.now())

            embed = set_success_marry(self.ctx, self.member)
            await interaction.response.edit_message(embed=embed, view=View())

    @button(label='Нет', custom_id='btn_no')
    async def button_callback_no(self, button, interaction):
        embed = set_refusal_wedding(self.ctx, self.member)
        await interaction.response.edit_message(embed=embed, view=View())
    
    async def on_timeout(self):
        return