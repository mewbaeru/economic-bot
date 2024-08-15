from disnake import Option
from disnake.ext import commands, tasks
from disnake.ui import Select

from database.requests import get_balance, is_exists_role, get_all_roles, get_time_to_pay, delete_role, get_give_by_owner, is_exists_role_in_shop, get_cost_role_in_shop
from modules import *

guild_id = Utils.get_guild_id()

# get role data from settings
try: 
    settings_roles, settings_prices = Utils.get_personal_roles()
except Exception:
    logger.error('failed to load settings')

class PersonalRoles(commands.Cog):
    def __init__(self, client):
        self.client = client

    # role
    @commands.slash_command(name='role', guild_ids=[guild_id])
    async def role(self, interaction):
        pass
    
    # role create
    @role.sub_command(name='create', description='Создание личной роли', 
                      options=[ 
                          Option(name='name', description='Введите название личной роли', required=True, max_length=100),
                          Option(name='color', description='Введите цвет личной роли в формате HEX (#FFFFFF)', required=True, max_length=7)
                          ]   
    )
    async def create(self, ctx, name: str, color: str):
        if await get_balance(ctx.author.id) >= settings_prices.get('role_create'):
            try:
                colour = await commands.ColourConverter().convert(ctx, color)
            except Exception:
                embed = set_invalid_color()
                await ctx.response.send_message(embed=embed, ephemeral=True)
                return
        else:
            embed = set_invalid_money()
            await ctx.response.send_message(embed=embed, ephemeral=True)
            return
        
        await ctx.response.defer()
        
        # role creation confirmation
        embed = set_role_creation_confirmation(ctx, name, colour, settings_prices.get('role_create'))
        await ctx.send(embed=embed, view=RoleConfirmationView(ctx, name, colour, settings_roles, settings_prices))
    
    # role manage
    @role.sub_command(name='manage', description='Управление личной ролью')
    async def manage(self, ctx):
        if await is_exists_role(ctx.author.id):
            await ctx.response.defer()
            embed = set_manage_role(ctx)

            # menu for choose a role
            select_menu = Select(placeholder='Выберите настраиваемую роль', max_values=1)
            roles = await get_all_roles(ctx.author.id)

            for role in roles:
                n_role = disnake.utils.get(ctx.guild.roles, id=role)
                select_menu.add_option(label=f'{n_role.name}', value=f'{n_role.id}')
            
            async def callback(interaction):
                role = disnake.utils.get(ctx.guild.roles, id=int(select_menu.values[0]))
                time_pay = await get_time_to_pay(ctx.author.id)
                shop_status = await is_exists_role_in_shop(role.id)
                shop_cost = await get_cost_role_in_shop(role.id)
                
                embed = set_edit_role(ctx, role, await get_give_by_owner(role.id), time_pay, settings_prices.get('role_create'), shop_status, shop_cost)
                await interaction.response.edit_message(embed=embed, view=RolesEdit(ctx, role, time_pay, shop_cost, shop_status, settings_roles, settings_prices))

            select_menu.callback = callback
            view = View()
            view.add_item(select_menu)
            await ctx.send(embed=embed, view=view)
        else:
            embed = set_not_roles(ctx)
            await ctx.send(embed=embed, ephemeral=True, view=View())

    @tasks.loop(hours=24)
    async def monthly_payment(self, ctx):
        if await is_exists_role(ctx.author.id):
            if datetime.now() >= await get_time_to_pay(ctx.author.id):
                if await get_balance(ctx.author.id) >= settings_prices.get('role_create'):
                    await take_money(ctx.author.id, settings_prices.get('role_create'))
                else:
                    await delete_role(ctx.author.id)

def setup(client):
    client.add_cog(PersonalRoles(client))