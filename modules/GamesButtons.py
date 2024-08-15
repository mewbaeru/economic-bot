import asyncio
from disnake.ui import View, button, Button

from modules.Logger import *
from modules.Embeds import *
from database.requests import take_money, give_money, get_balance, add_transaction

import random
from datetime import datetime

# coinflip
class CoinflipView(View):
    def __init__(self, ctx, amount, utils, timeout=60):
        super().__init__(timeout=timeout)
        self.ctx = ctx
        self.amount = amount
        self.utils = utils
        self.determine_flip = ['Орел', 'Решка']
    
    @button(label='Орел', custom_id='btn_heads')
    async def button_callback_heads(self, button, interaction):
        await self.handle_game(interaction, 'Орел')

    @button(label='Решка', custom_id='btn_tails')
    async def button_callback_tails(self, button, interaction):
        await self.handle_game(interaction, 'Решка')
    
    async def on_timeout(self):
        if self.ctx.author.id in self.utils.ActiveGames:
            self.utils.stop_game(self.ctx.author.id)
        return
    
    async def handle_game(self, interaction, chosen_side):
        if self.ctx.author.id == interaction.user.id:
            embed = set_process_coinflip(self.ctx, chosen_side, self.amount)
            await interaction.response.edit_message(embed=embed, view=View())

            await asyncio.sleep(3)

            random_win = random.choice(self.determine_flip)
            await self.process_result(interaction, random_win, chosen_side)

    async def process_result(self, interaction, random_win, chosen_side):
        view = View()
        button_repeat_game = Button(label='Сыграть с той же ставкой', custom_id='btn_repeat_game')
        button_repeat_game.callback = self.button_callback_repeat_game
        view.add_item(button_repeat_game)

        if random_win == chosen_side:
            await give_money(self.ctx.author.id, self.amount * 2)
            
            logger.info(f'/coinflip - player: {self.ctx.author.id} - award: {self.amount * 2}')
            # add new transaction
            await add_transaction(self.ctx.author.id, f'Игра в монетку', +self.amount * 2, datetime.now())

            embed = set_win_coinflip(self.ctx, self.amount, await get_balance(self.ctx.author.id))
        else:
            await take_money(self.ctx.author.id, self.amount)

            logger.info(f'/coinflip - player: {self.ctx.author.id} - defeat: {self.amount}')
            # add new transaction
            await add_transaction(self.ctx.author.id, f'Игра в монетку', -self.amount, datetime.now())

            embed = set_lose_coinflip(self.ctx, self.amount, await get_balance(self.ctx.author.id))
        await interaction.edit_original_response(embed=embed, view=view)
        self.utils.stop_game(self.ctx.author.id)
    
    async def button_callback_repeat_game(self, interaction):
        if self.ctx.author.id == interaction.user.id:
            self.utils.start_game(self.ctx.author.id)
            embed = set_coinflip(self.ctx, self.amount)
            await interaction.response.edit_message(embed=embed, view=self)

# duel
class DuelView(View):
    def __init__(self, ctx, opponent, amount, utils, timeout=60):
        super().__init__(timeout=timeout)
        self.ctx = ctx
        self.opponent = opponent
        self.amount = amount
        self.utils = utils
    
    @button(label='Присоединиться', custom_id='btn_join')
    async def button_callback_join(self, button, interaction):
        if self.opponent is not None:
            if self.opponent == interaction.user:
                await self.handle_game_duel(interaction)
        elif self.opponent is None:
            self.opponent = interaction.user
            await self.handle_game_duel(interaction)

    @button(label='Отмена', custom_id='btn_delete')
    async def button_callback_delete_game(self, button, interaction):
        if self.ctx.author.id == interaction.user.id:
            self.utils.stop_game(self.ctx.author.id)
            await interaction.message.delete()
    
    async def on_timeout(self):
        if self.ctx.author.id in self.utils.ActiveGames:
            self.utils.stop_game(self.ctx.author.id)
        return
    
    async def handle_game_duel(self, interaction):
        if await get_balance(self.opponent.id) >= self.amount * 2:
            embed = set_process_duel(self.ctx, self.opponent, self.amount)
            await interaction.response.edit_message(embed=embed, view=View())

            await asyncio.sleep(3)

            winner = random.choice([self.ctx.author, self.opponent])
            loser = self.ctx.author if winner == self.opponent else self.opponent
            await self.process_result(interaction, winner, loser)
        else:
            self.utils.stop_game(self.ctx.author.id)
            embed = set_invalid_money_member(self.opponent, 'Сыграть дуэль', await get_balance(self.opponent.id))
            await interaction.send(embed=embed, ephemeral=True, user=self.opponent)
    
    async def process_result(self, interaction, winner, loser):
        await give_money(winner.id, self.amount * 2)
        await take_money(loser.id, self.amount)

        embed = set_win_duel(self.ctx, winner, loser, self.amount)
        await interaction.edit_original_response(embed=embed, view=View())

        logger.info(f'/duel - winner {winner.id} - loser {loser.id} - amount {self.amount}')
        # add new transaction
        await add_transaction(winner.id, f'Дуэль против пользователя {loser}', +self.amount, datetime.now())
        await add_transaction(loser.id, f'Дуэль против пользователя {winner}', -self.amount, datetime.now())
        
        self.utils.stop_game(self.ctx.author.id)