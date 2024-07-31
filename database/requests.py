import disnake
from sqlalchemy import select, delete, update

from modules.Logger import *
from database.models import async_session
from database.models import User, PersonalRole

from datetime import datetime, timedelta

'''Users'''

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

# last date to receive the award (timely)
async def get_daily_award(member_id: int):
    async with async_session() as session:
        result = await session.scalar(select(User.daily).where(User.id == member_id))
        return result if result is not None else 0

# update daily reward date
async def update_dayly_award(member_id: int, newdate: int):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.id == member_id))
        if user:
            user.daily = newdate
            await session.commit()

# tracking time until next daily reward
async def get_time_left(member_id: int):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.id == member_id))
        if user:
            time_left = timedelta() - (datetime.now() - datetime.fromtimestamp(user.daily))
            return time_left if time_left > timedelta(0) else timedelta(0)
        
# receiving money by the user -> add it to db
async def give_money(member_id: int, amount: int):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.id == member_id))
        if user:
            await session.execute(update(User).where(User.id == member_id).values(cash=user.cash + amount))
            await session.commit()

# current balance user
async def get_balance(member_id: int):
    async with async_session() as session:
        result = await session.scalar(select(User.cash).where(User.id == member_id))
        return result if result is not None else 0

# transfer of money between users
async def transfer_money(member_sender_id: int, member_recipient_id, amount: int):
    async with async_session() as session:
        member_sender_balance = await get_balance(member_sender_id)
        member_recipient_balance = await get_balance(member_recipient_id)

        await session.execute(update(User).where(User.id == member_sender_id).values(cash=member_sender_balance - amount))
        await session.execute(update(User).where(User.id == member_recipient_id).values(cash=member_recipient_balance + amount))
        await session.commit()

# write-off of money from user
async def take_money(member_id: int, amount: int):
    async with async_session() as session:
        await session.execute(update(User).where(User.id == member_id).values(cash=User.cash - amount))
        await session.commit()

'''Personal_roles'''

# add new role to db
async def add_role(member_id: int, role_id: int):
    async with async_session() as session:
        time_pay = datetime.now() + timedelta(days=30)
        role = await session.scalar(select(PersonalRole).where(PersonalRole.id == role_id))
        if not role:
            session.add(PersonalRole(id=role_id, owner=member_id, time=int(time_pay.timestamp())))
            await session.commit()

# check if user has role
async def is_exists_role(member_id: int):
    async with async_session() as session:
        result = await session.scalar(select(PersonalRole.id).where(PersonalRole.owner == member_id))
        return True if result is not None else False

# get user personal roles
async def get_all_roles(member_id: int):
    async with async_session() as session:
        results = await session.execute(select(PersonalRole.id).where(PersonalRole.owner == member_id))
        return results.scalars().all()
    
# get time to pay
async def get_time_to_pay(member_id: int):
    async with async_session() as session:
        result = await session.scalar(select(PersonalRole.time).where(PersonalRole.owner == member_id))
        return result if result is not None else 0

# delete personal role
async def delete_role(member_id: int):
    async with async_session() as session:
        role = await session.scalar(select(PersonalRole).where(PersonalRole.owner == member_id))
        await session.delete(role)
        await session.commit()