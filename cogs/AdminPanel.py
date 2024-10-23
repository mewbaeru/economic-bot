import disnake 
from disnake.ext import commands

from database.requests import get_balance
from modules import *

guild_id = Utils.get_guild_id()

# get role data from settings
try: 
    settings_roles, settings_prices = Utils.get_personal_roles()
except Exception:
    logger.error('failed to load settings')

class AdminPanel(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.utils = Utils()
        
    # admin panel
    @commands.slash_command(name='admin', guild_ids=[guild_id], default_member_permissions=disnake.Permissions(administrator=True))
    async def role(self, interaction):
        pass

    @role.sub_command(name='panel', description='Панель администратора')
    @commands.has_role(settings_roles.get('owners_role'))
    async def admin_panel(ctx, user: disnake.Member = commands.Param(default=None, description='Выберите пользователя для взаимодействия')):
        logger.debug('/admin panel - start')
        if user is None:
            user = ctx.author
        elif user.bot:
            embed = set_invalid_user(ctx, 'Панель администратора', 'бота')
            await ctx.response.send_message(embed=embed, ephemeral=True)
            return
        
        embed = set_admin_panel(ctx, user)
        await ctx.response.send_message(embed=embed, view=AdminPanelView(ctx, user, settings_roles))
    
    @admin_panel.error
    async def admin_panel_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            embed = set_error_admin_panel(ctx)
            await ctx.response.send_message(embed=embed, ephemeral=True)

def setup(client):
    client.add_cog(AdminPanel(client))