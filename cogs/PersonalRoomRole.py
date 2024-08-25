from disnake import Option
from disnake.ext import commands, tasks
from disnake.ui import Select

from database.requests import get_balance, is_exists_room, get_info_room, get_personal_room_data, get_time_to_pay_room, delete_room, update_time_to_pay_room, get_all_owners
from modules import *

guild_id = Utils.get_guild_id()

# get role data from settings
try: 
    settings_roles, settings_prices = Utils.get_personal_roles()
except Exception:
    logger.error('failed to load settings')

class PersonalRoomRole(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.monthly_payment.start()

    # room
    @commands.slash_command(name='room', guild_ids=[guild_id])
    async def role(self, interaction):
        pass

    # room create
    @role.sub_command(name='create', description='Создание личной комнаты', 
                      options=[ 
                          Option(name='name', description='Введите название личной комнаты', required=True, max_length=100),
                          Option(name='color', description='Введите цвет роли для личной комнаты в формате HEX (#FFFFFF)', required=True, max_length=7),
                          Option(name='members', description='Выберите лимит пользователей', required=True, choices=['5', '10', '15', '20'])
                          ]
    )
    async def create(self, ctx, name: str, color: str, members: str):
        logger.debug('/room create - start')
        
        room_prices = settings_prices.get('room_create')
        price_users_limit = settings_prices.get('users_limit')
        total_price = room_prices + price_users_limit[members]
        
        if not await is_exists_room(ctx.author.id):
            if await get_balance(ctx.author.id) >= total_price:
                try:
                    colour = await commands.ColourConverter().convert(ctx, color)
                except Exception:
                    embed = set_invalid_color(ctx)
                    await ctx.response.send_message(embed=embed, ephemeral=True)
                    return
            else:
                embed = set_error_money(ctx, total_price, await get_balance(ctx.author.id))
                await ctx.response.send_message(embed=embed, ephemeral=True)
                return
        else:
            embed = set_user_already_have_room(ctx)
            await ctx.response.send_message(embed=embed, ephemeral=True)
            return
        
        # role creation confirmation
        embed = set_room_creation_confirmation(ctx, name, total_price)
        await ctx.send(embed=embed, view=RoomConfirmationView(ctx, name, colour, members, total_price, settings_roles))
    
    # room manage
    @role.sub_command(name='manage', description='Управление личной комнатой')
    async def manage(self, ctx):
        logger.debug('/room manage - start')

        if await is_exists_room(ctx.author.id):
            personal_room_data = await get_personal_room_data(ctx.author.id)
            info_room = await get_info_room(ctx.author.id)

            role_room = disnake.utils.get(ctx.guild.roles, id=info_room[0])

            if personal_room_data['name'] != 0:
                room_name = personal_room_data['name']
            else:
                room_name = role_room.name

            embed = set_edit_room(ctx, room_name, role_room, co_owner=info_room[2], time_pay=info_room[3], members=role_room.members, 
                                  user_limit=info_room[4], cost_room_create=settings_prices.get('room_create'))
            await ctx.send(embed=embed, view=RoomsEdit(ctx, role_room, room_name, co_owner=info_room[2], time_pay=info_room[3],
                                                       members=role_room.members, user_limit=info_room[4], settings_prices=settings_prices))
        else:
            embed = set_not_room(ctx)
            await ctx.response.send_message(embed=embed, ephemeral=True)
            return
    
    # room info
    @role.sub_command(name='info', description='Информация о личной комнате')
    async def info(self, ctx, role: disnake.Role = commands.Param(description='Выберите роль личной комнаты')):
        if await is_exists_room(role.id):
            personal_room_data = await get_personal_room_data(role.id)
            info_room = await get_info_room(role.id)

            if personal_room_data['name'] != 0:
                room_name = personal_room_data['name']
            else:
                room_name = role.name
                
            embed = set_info_room(ctx, room_name=room_name, role=role, owner=info_room[1], co_owner=info_room[2], 
                                  time_pay=info_room[3], members=len(role.members))
            await ctx.send(embed=embed, view=RoomsInfo(ctx, role, owner=info_room[1], members=role.members, co_owner=info_room[2],
                                                                       time_pay=info_room[3], room_name=room_name))
        else:
            embed = set_invalid_info_room(ctx)
            await ctx.send(embed=embed, ephemeral=True, view=View())
    
    @tasks.loop(hours=24)
    async def monthly_payment(self):
        owners = await get_all_owners()
        if owners:
            for owner_id in owners:
                time_to_pay = await get_time_to_pay_room(owner_id)
                if time_to_pay and datetime.now() >= datetime.fromtimestamp(time_to_pay):
                    if await get_balance(owner_id) >= settings_prices.get('room_create'):
                        await update_time_to_pay_room(owner_id)
                        await take_money(owner_id, settings_prices.get('room_create'))

                        logger.info(f'/payment room - owner: {owner_id}')
                        # add new transaction
                        await add_transaction(owner_id, f'Оплата личной комнаты', -settings_prices.get('room_create'), datetime.now())
                    else:
                        await delete_room(owner_id)
                        logger.info(f'/payment room - delete room - owner: {owner_id}')
        else:
            logger.info(f'/payment room - no rooms')

def setup(client):
    client.add_cog(PersonalRoomRole(client))