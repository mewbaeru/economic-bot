from disnake.ext import commands

from database.requests import get_data_love_room, get_info_marriage, write_data_love_room
from modules import *

guild_id = Utils.get_guild_id()

# get channels data from settings
try: 
    settings_channels = Utils.get_channels()
except Exception:
    logger.error('failed to load settings')

class LoveRooms(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.utils = Utils

        self.guild = None
        self.member = None
        self.entry_love_room = None
        self.love_category = None 
        
    @commands.Cog.listener()
    async def on_ready(self):
        self.guild = self.client.get_guild(guild_id)

        self.entry_love_room = disnake.utils.get(self.guild.voice_channels, id=settings_channels.get('entry_love_room'))
        self.love_category = disnake.utils.get(self.guild.categories, id=settings_channels.get('love_category'))

        await self.check_love_rooms()
    
    # love rooms
    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if (before.channel != self.entry_love_room and after.channel == self.entry_love_room):
            self.member = member
            # if channel has already been created
            love_room_data = await get_data_love_room(self.member.id)

            if love_room_data['id'] != 0:
                channel = disnake.utils.get(self.guild.channels, id=love_room_data['id'])
                await self.member.edit(voice_channel=channel)
                return
            
            # create channel
            bitrates = [96000, 128000, 256000, 384000]
            bitrate = bitrates[self.guild.premium_tier]

            data = await get_info_marriage(self.member.id)

            partner_1 = self.client.get_user(data[0])
            partner_2 = self.client.get_user(data[1])

            overwrites = {
                self.guild.default_role: disnake.PermissionOverwrite(connect=False, view_channel=True),
                partner_1: disnake.PermissionOverwrite(connect=True, view_channel=True),
                partner_2: disnake.PermissionOverwrite(connect=True, view_channel=True),
            }

            custom_name = love_room_data['name']

            if custom_name != 0:
                channel_name = f'{custom_name}'
            else:
                channel_name = f'{partner_1.display_name} 💕 {partner_2.display_name}'
            channel = await self.guild.create_voice_channel(channel_name, bitrate=bitrate, overwrites=overwrites, category=self.love_category)

            await write_data_love_room(self.member.id, 'id', channel.id)
            await self.member.edit(voice_channel=channel)

    async def check_love_rooms(self):
        while True:
            channels_in_category = self.love_category.voice_channels
            for channel in channels_in_category:
                if channel != self.entry_love_room and not channel.members:
                        await write_data_love_room(self.member.id, 'id', 0)
                        await channel.delete(reason='empty channel')
            await asyncio.sleep(5)

def setup(client):
    client.add_cog(LoveRooms(client))