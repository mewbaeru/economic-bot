from disnake.ext import commands

from database.requests import get_info_room, write_data_personal_room, get_personal_room_data, get_all_personal_rooms_roles
from modules import *

guild_id = Utils.get_guild_id()

# get channels data from settings
try: 
    settings_channels = Utils.get_channels()
except Exception:
    logger.error('failed to load settings')

class PersonalRooms(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.utils = Utils

        self.guild = None
        self.entry_personal_room = None
        self.personal_room_category = None 

    @commands.Cog.listener()
    async def on_ready(self):
        self.guild = self.client.get_guild(guild_id)
        
        self.entry_personal_room = disnake.utils.get(self.guild.voice_channels, id=settings_channels.get('entry_personal_room'))
        self.personal_room_category = disnake.utils.get(self.guild.categories, id=settings_channels.get('personal_room_category'))

        await self.check_personal_rooms()
    
    # personal rooms
    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        roles_id = await get_all_personal_rooms_roles()
        if roles_id:
            for role_id in roles_id:
                self.role = disnake.utils.get(member.guild.roles, id=role_id)
                if self.role in member.roles:
                    if (before.channel != self.entry_personal_room and after.channel == self.entry_personal_room):
                        # if channel has already been created
                        personal_room_data = await get_personal_room_data(self.role.id)

                        if personal_room_data['id'] != 0:
                            channel = disnake.utils.get(self.guild.channels, id=personal_room_data['id'])
                            await member.edit(voice_channel=channel)
                            return
                    
                        # create channel
                        bitrates = [96000, 128000, 256000, 384000]
                        bitrate = bitrates[self.guild.premium_tier]

                        overwrites = {
                        self.guild.default_role: disnake.PermissionOverwrite(connect=False, view_channel=False),
                        self.role: disnake.PermissionOverwrite(connect=True, view_channel=True)
                        }

                        custom_name = personal_room_data['name']

                        if custom_name != 0:
                            room_name = custom_name
                        else:
                            room_name = self.role.name
                        channel = await self.guild.create_voice_channel(room_name, bitrate=bitrate, overwrites=overwrites, category=self.personal_room_category)
                        
                        await write_data_personal_room(self.role.id, 'id', channel.id)
                        await member.edit(voice_channel=channel)

    async def check_personal_rooms(self):
        while True:
            channels_in_category = self.personal_room_category.voice_channels
            for channel in channels_in_category:
                if channel != self.entry_personal_room and not channel.members:
                    roles_id = await get_all_personal_rooms_roles()
                    for role_id in roles_id:
                        personal_room_data = await get_personal_room_data(role_id)
                        if personal_room_data['id'] == channel.id:
                            await write_data_personal_room(role_id, 'id', 0)
                            await channel.delete(reason='empty channel')
            await asyncio.sleep(5)

def setup(client):
    client.add_cog(PersonalRooms(client))