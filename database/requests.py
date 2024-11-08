import disnake
from sqlalchemy import func, desc
from sqlalchemy import select, update, or_

from modules.Logger import *
from database.models import async_session
from database.models import User, PersonalRole, Marriage, Transaction, PersonalRoom, VoiceActivity

import json
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

# get count user's messages
async def get_count_messages(member_id: int):
    async with async_session() as session:
        result = await session.scalar(select(User.count_messages).where(User.id == member_id))
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

# get active marry
async def get_marry(member_id: int):
    async with async_session() as session:
        result = await session.scalar(select(User.marry).where(User.id == member_id))
        return result

# get clan membership
async def get_clan_membership(member_id: int):
    async with async_session() as session:
        result = await session.scalar(select(User.clan).where(User.id == member_id))
        return result
    
# get balance users for top
async def get_top_user_balance(member_id: int):
    async with async_session() as session:
        results = await session.execute(select(User.id, User.cash).order_by(desc(User.cash)))
        results = results.all()

        rank = None
        for i, user in enumerate(results):
            if user.id == member_id:
                rank = i + 1
                break

        return results[:10], rank

# get messages users for top
async def get_top_user_messages(member_id: int):
    async with async_session() as session:
        results = await session.execute(select(User.id, User.count_messages).order_by(desc(User.count_messages)))
        results = results.all()

        rank = None
        for i, user in enumerate(results):
            if user.id == member_id:
                rank = i + 1
                break

        return results[:10], rank

# remove user from db
async def remove_user(member: disnake.Member):
    async with async_session() as session:
        if not member.bot:
            user = await session.scalar(select(User).where(User.id == member.id))
            if user:
                user_marriage = await session.scalar(select(Marriage).where(or_(Marriage.partner_1 == member.id, Marriage.partner_2 == member.id)))
                if user_marriage:
                    await session.delete(user_marriage)

                user_personal_roles = await session.scalar(select(PersonalRole).where(PersonalRole.owner == member.id))
                if user_personal_roles:
                    await session.delete(user_personal_roles)

                user_personal_room = await session.scalar(select(PersonalRoom).where(PersonalRoom.owner == member.id))
                if user_personal_room:
                    await session.delete(user_personal_room)

                user_transactions = await session.scalar(select(Transaction).where(Transaction.member_id == member.id))
                if user_transactions:
                    await session.delete(user_transactions)

                await session.delete(user)
                await session.commit()

'''Voice activity'''

# add user voice activity
async def add_user_voice_activity(member: disnake.Member):
    if not member.bot:
        async with async_session() as session:
            user = await session.scalar(select(VoiceActivity).where(VoiceActivity.id == member.id))

            if not user:
                session.add(VoiceActivity(id=member.id))
                await session.commit()

# record the user's action
async def user_set_action_channel(member_id: int, action: str):
    async with async_session() as session:
        if action == 'join':
            await session.execute(update(VoiceActivity).where(VoiceActivity.id == member_id).values(joined_at=int(datetime.timestamp(datetime.now()))))
        elif action == 'left':
            await session.execute(update(VoiceActivity).where(VoiceActivity.id == member_id).values(left_at=int(datetime.timestamp(datetime.now()))))
        await session.commit()

# get user data of voice activity
async def get_user_voice_activity_data(member_id: int):
    async with async_session() as session:
        results = await session.execute(select(VoiceActivity.joined_at, VoiceActivity.left_at, VoiceActivity.total_minutes, VoiceActivity.total_hours).where(VoiceActivity.id == member_id))
        return results.first()
    
# update user data of voice activity
async def update_user_voice_activity(id: int, type: str, total_hours: int, total_minutes: int):
    async with async_session() as session:
        if type == 'default':
            await session.execute(update(VoiceActivity).where(VoiceActivity.id == id).values(total_minutes=total_minutes, total_hours=total_hours))
        elif type == 'love':
            love_room_data = await get_data_love_room(id)

            love_room_data['joined_at'] = 0
            love_room_data['total_hours'] = total_hours
            love_room_data['total_minutes'] = total_minutes

            await session.execute(update(Marriage).where(or_(Marriage.partner_1 == id, Marriage.partner_2 == id)).values(love_room=json.dumps(love_room_data)))
            await session.execute(update(VoiceActivity).where(VoiceActivity.id == id).values(total_minutes=total_minutes, total_hours=total_hours))
        elif type == 'room':
            personal_room_data = await get_personal_room_data(id)

            personal_room_data['joined_at'] = 0
            personal_room_data['total_hours'] = total_hours
            personal_room_data['total_minutes'] = total_minutes

            await session.execute(update(PersonalRoom).where(PersonalRoom.id == id).values(personal_room=json.dumps(personal_room_data)))
            await session.execute(update(VoiceActivity).where(VoiceActivity.id == id).values(total_minutes=total_minutes, total_hours=total_hours))
        await session.commit()

# remove the user's data about logging into channel
async def null_user_dates(member_id: int):
    async with async_session() as session:
        await session.execute(update(VoiceActivity).where(VoiceActivity.id == member_id).values(joined_at=0, left_at=0))
        await session.commit()

# get voice activity users for top
async def get_top_user_online(member_id: int):
    async with async_session() as session:
        results = await session.execute(select(VoiceActivity.id, VoiceActivity.total_hours, VoiceActivity.total_minutes).order_by(desc(VoiceActivity.total_hours), desc(VoiceActivity.total_minutes)))
        results = results.all()

        rank = None
        for i, user in enumerate(results):
            if user.id == member_id:
                rank = i + 1
                break

        return results[:10], rank

# delete user's voice activity
async def remove_user_voice_activity(member: disnake.Member):
    if not member.bot:
        async with async_session() as session:
            result = await session.scalar(select(VoiceActivity).where(VoiceActivity.id == member.id))
            if result:
                await session.delete(result)
                await session.commit()

'''Marriages'''

async def add_new_marriage(member_id_1: int, member_id_2: int):
    async with async_session() as session:
        time_create = datetime.now()
        time_pay = time_create + timedelta(days=30)
        room = {"name": 0, "total_hours": 0, "total_minutes": 0, "joined_at": 0, "id": 0}

        marriage = await session.scalar(select(Marriage).where(Marriage.partner_1 == member_id_1, Marriage.partner_2 == member_id_2))
        if not marriage:
            session.add(Marriage(partner_1=member_id_1, partner_2=member_id_2, time=int(time_pay.timestamp()), balance=0, 
                                 reg_marry=int(time_create.timestamp()), love_room=json.dumps(room)))
            await session.execute(update(User).where(or_(User.id == member_id_1, User.id == member_id_2)).values(marry=True))
            await session.execute(update(User).where(or_(User.id == member_id_1, User.id == member_id_2)).values(marry=True))
            await session.commit()

async def write_data_love_room(member_id: int, type: str, value: int):
    async with async_session() as session:
        love_room_data = await get_data_love_room(member_id)
        love_room_data[type] = value
        await session.execute(update(Marriage).where(or_(Marriage.partner_1 == member_id, Marriage.partner_2 == member_id)).values(love_room=json.dumps(love_room_data)))
        await session.commit()

async def get_data_love_room(member_id: int):
    async with async_session() as session:
        room = await session.scalar(select(Marriage.love_room).where(or_(Marriage.partner_1 == member_id, Marriage.partner_2 == member_id)))
        love_room_data = json.loads(room)
        return love_room_data

async def get_info_marriage(member_id: int):
    async with async_session() as session:
        results = await session.execute(select(Marriage.partner_1, Marriage.partner_2, Marriage.balance, Marriage.reg_marry, Marriage.love_room).where(or_(Marriage.partner_1 == member_id, Marriage.partner_2 == member_id)))
        return results.first()
    
# get voice activity for top
async def get_top_marriage_online(member_id: int):
    async with async_session() as session:
        results = await session.execute(select(Marriage.partner_1, Marriage.partner_2, func.json_extract(Marriage.love_room, "$.total_hours").label("total_hours"), func.json_extract(Marriage.love_room, "$.total_minutes").label("total_minutes")).order_by(desc("total_hours"), desc("total_minutes")))
        results = results.all()

        rank = None
        for i, user in enumerate(results):
            if user.partner_1 == member_id or user.partner_2 == member_id:
                rank = i + 1
                break

        return results[:10], rank

# update love room balance
async def update_love_room_balance(member_id: int, amount: int):
    async with async_session() as session:
        await session.execute(update(Marriage).where(or_(Marriage.partner_1 == member_id, Marriage.partner_2 == member_id)).values(balance=Marriage.balance+amount))
        await session.commit()

# divorce marriage 
async def divorce_marriage(id: int):
    async with async_session() as session:
        marriage = await session.scalar(select(Marriage).where(or_(Marriage.partner_1 == id, Marriage.partner_2 == id, Marriage.id == id)))
        await session.delete(marriage)

        partner_1 = marriage.partner_1
        partner_2 = marriage.partner_2

        await session.execute(update(User).where(or_(User.id == partner_1, User.id == partner_2)).values(marry=False))
        await session.execute(update(User).where(or_(User.id == partner_1, User.id == partner_2)).values(marry=False))

        await session.commit()

# get all marriages for payment 
async def get_all_marriages():
    async with async_session() as session:
        results = await session.scalars(select(Marriage.id).distinct())
        results = results.all()
        return results if results else False

# get time to pay
async def get_time_to_pay_love_room(marriage_id: int):
    async with async_session() as session:
        result = await session.scalar(select(Marriage.time).where(Marriage.id == marriage_id))
        return result

# get love room balance 
async def get_balance_love_room(marriage_id: int):
    async with async_session() as session:
        result = await session.scalar(select(Marriage.balance).where(Marriage.id == marriage_id))
        return result

# update time to pay
async def update_time_to_pay_love_room(marriage_id: int):
    async with async_session() as session:
        new_time = datetime.now() + timedelta(days=30)
        await session.execute(update(Marriage).where(Marriage.id == marriage_id).values(time=int(new_time.timestamp())))
        await session.commit()

# take money from balance love room
async def take_money_love_room(marriage_id: int, amount: int):
    async with async_session() as session:
        await session.execute(update(Marriage).where(Marriage.id == marriage_id).values(balance=Marriage.balance - amount))
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

# get all personal roles on guild
async def get_all_owners_personal_roles():
    async with async_session() as session:
        results = await session.scalars(select(PersonalRole.owner).distinct())
        results = results.all()
        return results if results else False
    
# get user personal roles
async def get_all_roles_users(member_id: int):
    async with async_session() as session:
        results = await session.execute(select(PersonalRole.id).where(PersonalRole.owner == member_id))
        return results.scalars().all()

# get time to pay
async def get_time_to_pay(role_id: int):
    async with async_session() as session:
        result = await session.scalar(select(PersonalRole.time).where(PersonalRole.id == role_id))
        return result

# update time to pay
async def update_time_to_pay(role_id: int):
    async with async_session() as session:
        new_time = datetime.now() + timedelta(days=30)
        await session.execute(update(PersonalRole).where(PersonalRole.id == role_id).values(time=int(new_time.timestamp())))
        await session.commit()

# add role given by owner
async def add_give_by_owner(role_id: int, member_id: str):
    async with async_session() as session:
        result = await session.execute(select(PersonalRole.give_by_owner).where(PersonalRole.id == role_id))
        current_list = result.scalar_one_or_none() or []
        current_list.append(f'<@{member_id}>')
        await session.execute(update(PersonalRole).where(PersonalRole.id == role_id).values(give_by_owner=current_list))
        await session.commit()

# get user with role give by owner
async def get_give_by_owner(role_id: int):
    async with async_session() as session:
        results = await session.execute(select(PersonalRole.give_by_owner).where(PersonalRole.id == role_id))
        results = results.scalar_one_or_none() or []
        return 0 if not results else results

# get len user with role give by owner
async def get_len_user_give_by_owner(role_id: int):
    async with async_session() as session:
        results = await session.execute(select(PersonalRole.give_by_owner).where(PersonalRole.id == role_id))
        results = results.scalar_one_or_none() or []
        return 0 if not results else len(results)
    
# delete role from list give by owner
async def delete_give_by_owner(role_id: int, member_id: str):
    async with async_session() as session:
        result = await session.execute(select(PersonalRole.give_by_owner).where(PersonalRole.id == role_id))
        current_list = result.scalar_one_or_none() or []
        if f'<@{member_id}>' in current_list:
            current_list.remove(f'<@{member_id}>')
            await session.execute(update(PersonalRole).where(PersonalRole.id == role_id).values(give_by_owner=current_list))
            await session.commit()

# delete personal role
async def delete_role(role_id: int):
    async with async_session() as session:
        role = await session.scalar(select(PersonalRole).where(PersonalRole.id == role_id))
        await session.delete(role)
        await session.commit()

# add role in shop
async def add_role_to_shop(role_id: int, shop_cost: int):
    async with async_session() as session:
        await session.execute(update(PersonalRole).where(PersonalRole.id == role_id).values(shop=True, shop_cost=shop_cost))
        await session.commit()

# add count user which buy role
async def add_count_user(role_id: int):
    async with async_session() as session:
        count_user = await session.scalar(select(PersonalRole.count_user).where(PersonalRole.id == role_id))
        new_count = count_user + 1
        await session.execute(update(PersonalRole).where(PersonalRole.id == role_id).values(count_user=new_count))
        await session.commit()
    
# check if role in shop
async def is_exists_role_in_shop(role_id: int):
    async with async_session() as session:
        result = await session.scalar(select(PersonalRole.shop).where(PersonalRole.id == role_id))
        return result
    
# get cost role in shop
async def get_cost_role_in_shop(role_id: int):
    async with async_session() as session:
        result = await session.scalar(select(PersonalRole.shop_cost).where(PersonalRole.id == role_id))
        return result

# delete role from shop
async def delete_role_from_shop(role_id: int):
    async with async_session() as session:
        await session.execute(update(PersonalRole).where(PersonalRole.id == role_id).values(shop=False, shop_cost=0))
        await session.commit()
        
# get roles in shop 
async def get_shop_roles():
    async with async_session() as session:
        roles = await session.execute(select(PersonalRole.id, PersonalRole.time, PersonalRole.owner, PersonalRole.shop_cost, PersonalRole.count_user).where(PersonalRole.shop == True))
        roles = roles.all()
        return roles

# change cost role in roles shop
async def change_cost_role_in_shop(role_id: int, new_shop_cost: int):
    async with async_session() as session:
        await session.execute(update(PersonalRole).where(PersonalRole.id == role_id).values(shop_cost=new_shop_cost))
        await session.commit()

'''Personal rooms'''

# add new personal room
async def add_room(member_id: int, role_id: int, members: str):
    async with async_session() as session:
        time_pay = datetime.now() + timedelta(days=30)
        room = {"name": 0, "total_hours": 0, "total_minutes": 0, "joined_at": 0, "id": 0}

        personal_room = await session.scalar(select(PersonalRoom).where(PersonalRoom.id == role_id))
        if not personal_room:
            session.add(PersonalRoom(id=role_id, owner=member_id, time=int(time_pay.timestamp()), limit=members, personal_room=json.dumps(room)))
            await session.commit()

# get all owners for payment 
async def get_all_owners():
    async with async_session() as session:
        results = await session.scalars(select(PersonalRoom.owner).distinct())
        results = results.all()
        return results if results else False

# if exists personal room role
async def get_all_personal_rooms_roles():
    async with async_session() as session:
        results = await session.scalars(select(PersonalRoom.id).distinct())
        results = results.all()
        return results if results else False
    
# if personal room is exists
async def is_exists_room(id: int):
    async with async_session() as session:
        result = await session.scalar(select(PersonalRoom).where(or_(PersonalRoom.owner == id, PersonalRoom.co_owner == id, PersonalRoom.id == id)))
        return True if result is not None else False

# if personal room owner is exists
async def is_exists_room_owner(member_id: int):
    async with async_session() as session:
        result = await session.scalar(select(PersonalRoom).where(PersonalRoom.owner == member_id))
        return True if result is not None else False
    
# get all rooms users where he is owner and co-owner
async def get_all_rooms_user(member_id: int):
    async with async_session() as session:
        results = await session.execute(select(PersonalRoom.id).where(or_(PersonalRoom.owner == member_id, PersonalRoom.co_owner == member_id)))
        return results.scalars().all()
    
# get data personal room
async def get_info_room(id: int):
    async with async_session() as session:
        results = await session.execute(select(PersonalRoom.id, PersonalRoom.owner, PersonalRoom.co_owner, PersonalRoom.time, PersonalRoom.limit).where(or_(PersonalRoom.owner == id, PersonalRoom.co_owner == id, PersonalRoom.id == id)))
        return results.first()

# get role room id by owner
async def get_personal_room_role_id(member_id: int):
    async with async_session() as session:
        result = await session.scalar(select(PersonalRoom.id).where(PersonalRoom.owner == member_id))
        return result if result else False
    
# get data voice channel
async def get_personal_room_data(id: int):
    async with async_session() as session:
        room =  await session.scalar(select(PersonalRoom.personal_room).where(or_(PersonalRoom.owner == id, PersonalRoom.co_owner == id, PersonalRoom.id == id)))
        personal_room_data = json.loads(room)
        return personal_room_data

# write new data to personal room
async def write_data_personal_room(id: int, type: str, value: int):
    async with async_session() as session:
        personal_room_data = await get_personal_room_data(id)
        personal_room_data[type] = value
        await session.execute(update(PersonalRoom).where(PersonalRoom.id == id).values(personal_room=json.dumps(personal_room_data)))
        await session.commit()

# change room name in db
async def update_room_name(member_id: int, type: str, value: str):
    async with async_session() as session:
        personal_room_data = await get_personal_room_data(member_id)
        personal_room_data[type] = value
        await session.execute(update(PersonalRoom).where(or_(PersonalRoom.owner == member_id, PersonalRoom.co_owner == member_id)).values(personal_room=json.dumps(personal_room_data)))
        await session.commit()

# get user limit
async def get_user_limit(id: int):
    async with async_session() as session:
        result = await session.scalar(select(PersonalRoom.limit).where(PersonalRoom.id == id))
        return result
    
# update user limit
async def update_user_limit(member_id: int, new_limit: str):
    async with async_session() as session:
        await session.execute(update(PersonalRoom).where(PersonalRoom.owner == member_id).values(limit=new_limit))
        await session.commit()

# get room owner
async def get_room_owner(member_id):
    async with async_session() as session:
        result = await session.scalar(select(PersonalRoom.owner).where(or_(PersonalRoom.owner == member_id, PersonalRoom.co_owner == member_id)))
        return result
    
# get co_owner
async def get_room_co_owner(member_id: int):
    async with async_session() as session:
        result = await session.scalar(select(PersonalRoom.co_owner).where(PersonalRoom.owner == member_id))
        return result if result != 0 else False

# get time to pay
async def get_time_to_pay_room(member_id: int):
    async with async_session() as session:
        result = await session.scalar(select(PersonalRoom.time).where(PersonalRoom.owner == member_id))
        return result

# update time to pay
async def update_time_to_pay_room(member_id: int):
    async with async_session() as session:
        new_time = datetime.now() + timedelta(days=30)
        await session.execute(update(PersonalRoom).where(PersonalRoom.owner == member_id).values(time=int(new_time.timestamp())))
        await session.commit()
    
# add new co-owner
async def add_co_owner(member_id: int, co_owner: int):
    async with async_session() as session:
        await session.execute(update(PersonalRoom).where(PersonalRoom.owner == member_id).values(co_owner=co_owner))
        await session.commit()

# delete co-owner
async def delete_co_owner(member_id: int):
    async with async_session() as session:
        await session.execute(update(PersonalRoom).where(PersonalRoom.owner == member_id).values(co_owner=0))
        await session.commit()

# delete room
async def delete_room(member_id: int):
    async with async_session() as session:
        room = await session.scalar(select(PersonalRoom).where(PersonalRoom.owner == member_id))
        await session.delete(room)
        await session.commit()

# change owner 
async def add_new_owner(member_id: int, new_owner: int):
    async with async_session() as session:
        await session.execute(update(PersonalRoom).where(PersonalRoom.owner == member_id).values(owner=new_owner))
        await session.commit()

# if user already owner
async def is_user_already_owner(member_id: int):
    async with async_session() as session:
        result = await session.scalar(select(PersonalRoom).where(PersonalRoom.owner == member_id))
        return True if result is not None else False

# get voice activity for top
async def get_top_personal_room_online(member_id: int):
    async with async_session() as session:
        results = await session.execute(select(PersonalRoom.id, PersonalRoom.owner, func.json_extract(PersonalRoom.personal_room, "$.total_hours").label("total_hours"), func.json_extract(PersonalRoom.personal_room, "$.total_minutes").label("total_minutes")).order_by(desc("total_hours"), desc("total_minutes")))
        results = results.all()

        rank = None
        for i, user in enumerate(results):
            if user.owner == member_id:
                rank = i + 1
                break

        return results[:10], rank
    
'''Transactions'''

# add transaction
async def add_transaction(member_id: int, category: str, value: int, time: int):
    async with async_session() as session:
        session.add(Transaction(member_id=member_id, category=category, value=value, time=int(time.timestamp())))
        await session.commit()

# check if user has transaction
async def is_exists_transaction(member_id: int):
    async with async_session() as session:
        result = await session.scalar(select(Transaction).where(Transaction.member_id == member_id))
        return True if result is not None else False

# get user transactions
async def get_user_transactions(member_id: int):
    async with async_session() as session:
        results = await session.execute(select(Transaction.category, Transaction.value, Transaction.time).where(Transaction.member_id == member_id))
        results = results.all()
        if len(results) > 100:
            last_transaction = await session.scalar(select(Transaction).where(Transaction.member_id == member_id).order_by(Transaction.time).limit(1))
            await session.delete(last_transaction)
            results = await session.execute(select(Transaction.category, Transaction.value, Transaction.time).where(Transaction.member_id == member_id))
            results = results.all()
        return results