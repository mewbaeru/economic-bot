from disnake.ui import View, button

from modules.Logger import *
from modules.Embeds import *

# transaction
class TransactionView(View):
    def __init__(self, ctx, user, page, transactions, total_pages, timeout=120):
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
        embed = set_transaction(self.user, self.transactions, self.page, self.total_pages)
        await interaction.response.edit_message(embed=embed, view=self)

    @button(label='≪', custom_id='back_transaction')
    async def button_back_transaction(self, button, interaction):
        if interaction.user.id == self.ctx.author.id:
            self.page -= 1
            await self.update_embed(interaction)
    
    @button(label='🗑️', custom_id='delete_transaction')
    async def buttin_delete_transaction(self, button, interaction):
        if interaction.user.id == self.ctx.author.id:
            await interaction.message.delete()

    @button(label='≫', custom_id='next_transaction')
    async def button_next_transaction(self, button, interaction):
        if interaction.user.id == self.ctx.author.id:
            self.page += 1
            await self.update_embed(interaction)