import disnake
from sqlalchemy import select, delete, update

from modules.Logger import *
from database.models import async_session
from database.models import User

# add user to db
async def add_user(member: disnake.Member):
    if not member.bot:
        async with async_session() as session:
            user = await session.scalar(select(User).where(User.id == member.id))

            if not user:
                session.add(User(id=member.id, name=member.name))
                await session.commit()

# update the user's messages in db
async def save_messages_count(dict: dict):
    if dict:
        async with async_session() as session:
            for member_id, count in dict.items():
                user = await session.scalar(select(User).where(User.id == member_id))
                if user:
                    user.count_messages += count
                    await session.commit()