from disnake import ButtonStyle
from disnake.ui import View, button

from modules.Logger import *
from modules.Embeds import *

# transaction
class TransactionView(View):
    def __init__(self, ctx, user, page, transactions, total_pages, timeout=60):
        super().__init__(timeout=timeout)
        self.ctx = ctx
        self.user = user
        self.page = page
        self.total_pages = total_pages
        self.transactions = transactions
    
    async def on_timeout(self):
        return
    
    async def update_embed(self, interaction):
        self.page = max(min(self.page, self.total_pages), 1)
        embed = set_transaction(self.ctx, self.user, self.transactions, self.page, self.total_pages)
        await interaction.response.edit_message(embed=embed, view=self)
    
    @button(emoji='<:arrow_1_mewbae:1276607084221300738>', custom_id='first_transation')
    async def first_transation(self, button, interaction):
        if interaction.user.id == self.ctx.author.id:
            self.page = 1
            await self.update_embed(interaction)

    @button(emoji='<:arrow_2_mewbae:1276607019528486985>', custom_id='back_transaction')
    async def button_back_transaction(self, button, interaction):
        if interaction.user.id == self.ctx.author.id:
            self.page -= 1
            await self.update_embed(interaction)
    
    @button(emoji='<:negative_squared_cross_mark_mewb:1276598003699814510>', custom_id='delete_transaction', style=ButtonStyle.red)
    async def buttin_delete_transaction(self, button, interaction):
        if interaction.user.id == self.ctx.author.id:
            await interaction.message.delete()

    @button(emoji='<:arrow_3_mewbae:1276607041288536095>', custom_id='next_transaction')
    async def button_next_transaction(self, button, interaction):
        if interaction.user.id == self.ctx.author.id:
            self.page += 1
            await self.update_embed(interaction)
    
    @button(emoji='<:arrow_4_mewbae:1276607061123137589>', custom_id='last_transaction')
    async def last_transaction(self, button, interaction):
        if interaction.user.id == self.ctx.author.id:
            self.page = self.total_pages
            await self.update_embed(interaction)