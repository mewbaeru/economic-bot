from disnake.ui import View, button

from database.requests import user_set_action_channel, get_user_voice_activity_data, update_user_voice_activity, null_user_dates, get_marry, get_data_love_room, get_info_marriage, write_data_love_room, get_all_personal_rooms_roles, get_personal_room_data, write_data_personal_room
from modules import *

from datetime import datetime

guild_id = Utils.get_guild_id()

class Tracker(commands.Cog):
    def __init__(self, client):
        self.client = client
    
    @commands.Cog.listener()
    async def on_ready(self):
        self.guild = self.client.get_guild(guild_id)

    async def leave_channel(self, member):
        await user_set_action_channel(member.id, 'left')

        user_data = await get_user_voice_activity_data(member.id)

        if user_data[0] != 0:
            join_time = datetime.fromtimestamp(int(user_data[0]))
            left_time = datetime.fromtimestamp(int(user_data[1]))

            new_time = left_time - join_time

            hours, remainder = divmod(new_time.seconds, 3600)
            minutes, seconds = divmod(remainder, 60)

            total_hours = hours + user_data[2]
            total_minutes = minutes + user_data[3]

            if total_minutes >= 60:
                total_minutes -= 60
                total_hours += 1
            
            await update_user_voice_activity(member.id, 'default', total_hours, total_minutes)
        await null_user_dates(member.id)
    
    async def leave_love_room_channel(self, member):
        if (await get_data_love_room(member))['joined_at'] != 0:
            join_time = datetime.fromtimestamp((await get_data_love_room(member))['joined_at'])
            left_time = datetime.fromtimestamp(int(datetime.timestamp(datetime.now())))

            new_time = left_time - join_time

            hours, remainder = divmod(new_time.seconds, 3600)
            minutes, seconds = divmod(remainder, 60)

            total_hours = hours + (await get_data_love_room(member))['total_hours']
            total_minutes = minutes + (await get_data_love_room(member))['total_minutes']

            if total_minutes >= 60:
                total_minutes -= 60
                total_hours += 1
            
            await update_user_voice_activity(member, 'love', total_hours, total_minutes)
        await null_user_dates(member)
    
    async def leave_personal_room_channel(self, member, role):
        if (await get_personal_room_data(role))['joined_at'] != 0:
            join_time = datetime.fromtimestamp((await get_personal_room_data(role))['joined_at'])
            left_time = datetime.fromtimestamp(int(datetime.timestamp(datetime.now())))

            new_time = left_time - join_time

            hours, remainder = divmod(new_time.seconds, 3600)
            minutes, seconds = divmod(remainder, 60)

            total_hours = hours + (await get_personal_room_data(role))['total_hours']
            total_minutes = minutes + (await get_personal_room_data(role))['total_minutes']

            if total_minutes >= 60:
                total_minutes -= 60
                total_hours += 1
            
            await update_user_voice_activity(role, 'room', total_hours, total_minutes)
        await null_user_dates(member)
    
    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        # user join channel
        if before.channel is None and after.channel is not None:
            await user_set_action_channel(member.id, 'join')

            # user join to love room
            if await get_marry(member.id):
                await asyncio.sleep(5)

                if after.channel.id == (await get_data_love_room(member.id))['id']:
                    verify = False

                    data = await get_info_marriage(member.id)

                    partner_1 = self.guild.get_member(data[0])
                    partner_2 = self.guild.get_member(data[1])

                    for member_in in after.channel.members:
                        if partner_1.id == member.id:
                            if member_in.id == partner_1.id:
                                verify = True
                        elif partner_2.id == member.id:
                            if member_in.id == partner_2.id:
                                verify = True

                    if verify:
                        await write_data_love_room(member.id, 'joined_at', int(datetime.timestamp(datetime.now())))
            
            # user join to personal room
            roles_id = await get_all_personal_rooms_roles()
            if roles_id:
                for role_id in roles_id:
                    role = disnake.utils.get(member.guild.roles, id=role_id)
                    if after.channel.id == (await get_personal_room_data(role.id))['id']:
                        verify = False

                        if role in member.roles:
                            verify = True
                        
                        if verify:
                            await write_data_personal_room(role.id, 'joined_at', int(datetime.timestamp(datetime.now())))

        # user left channel
        elif before.channel is not None and after.channel is None:
            await self.leave_channel(member)

            # user left love room
            if await get_marry(member.id):
                if before.channel.id == (await get_data_love_room(member.id))['id']:
                    await self.leave_love_room_channel(member.id)
            
            # user left personal room
            roles_id = await get_all_personal_rooms_roles()
            if roles_id:
                for role_id in roles_id:
                    role = disnake.utils.get(member.guild.roles, id=role_id)
                    if before.channel.id == (await get_personal_room_data(role.id))['id']:
                        await self.leave_personal_room_channel(member.id, role.id)
        
        # user switched channel
        elif before.channel is not None and after.channel is not None:
            # user switched channel to love room
            if await get_marry(member.id):
                if after.channel.id == (await get_data_love_room(member.id))['id']:
                    verify = False

                    data = await get_info_marriage(member.id)

                    partner_1 = self.guild.get_member(data[0])
                    partner_2 = self.guild.get_member(data[1])

                    for member_in in after.channel.members:
                        if partner_1 == member.id:
                            if member_in.id == partner_2:
                                verify = True
                        elif partner_2 == member.id:
                            if member_in.id == partner_1:
                                verify = True

                    if verify:
                        await write_data_love_room(member.id, 'joined_at', int(datetime.timestamp(datetime.now())))
                    elif after.channel.id != (await get_data_love_room(member.id))['id']:
                        await self.leave_love_room_channel(member.id)
            
            # user switched channel to personal room
            roles_id = await get_all_personal_rooms_roles()
            if roles_id:
                for role_id in roles_id:
                    role = disnake.utils.get(member.guild.roles, id=role_id)
                    if after.channel.id == (await get_personal_room_data(role.id))['id']:
                        verify = False

                        if role in member.roles:
                            verify = True
                        
                        if verify:
                            await write_data_personal_room(role.id, 'joined_at', int(datetime.timestamp(datetime.now())))
                        elif after.channel.id != (await get_personal_room_data(role.id))['id']:
                            await self.leave_personal_room_channel(member.id, role.id)

def setup(client):
    client.add_cog(Tracker(client))