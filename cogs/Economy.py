import disnake
from disnake.ext import commands, tasks

from database.requests import add_user, save_messages_count
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
        
        self.messages.start()

    # new member join -> add user to db
    @commands.Cog.listener()
    async def on_member_join(self, member):
        await add_user(member)
    
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