from disnake.ext import commands, tasks

from database.requests import add_user, add_user_voice_activity, save_messages_count, remove_user, remove_user_voice_activity
from modules import *

guild_id = Utils.get_guild_id()

class Economy(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.utils = Utils()
        
    # bot ready
    @commands.Cog.listener()
    async def on_ready(self):
        guild = self.client.get_guild(guild_id)
        members = guild.members

        for member in members:
            await add_user(member)
            await add_user_voice_activity(member)
        
        self.messages.start()

    # new member join -> add user to db
    @commands.Cog.listener()
    async def on_member_join(self, member):
        await add_user(member)
        await add_user_voice_activity(member)
    
    # member leaves -> remove user from db
    @commands.Cog.listener()
    async def on_member_remove(self, member):
        await remove_user(member)
        await remove_user_voice_activity(member)

    # message counter
    @tasks.loop(seconds=30)
    async def messages(self):
        await save_messages_count(self.utils.get_messages())
    
    @commands.Cog.listener()
    async def on_message(self, ctx):
        author = ctx.author.id
        
        self.utils.write_message(author)

        await self.client.process_commands(ctx)

def setup(client):
    client.add_cog(Economy(client))