from sqlalchemy import String, Boolean, Integer, JSON, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine

from typing import List
from modules.Logger import *

# creation and connection to the db
engine = create_async_engine(url='sqlite+aiosqlite:///db.sqlite3')
async_session = async_sessionmaker(engine)

class Base(AsyncAttrs, DeclarativeBase):
    pass

class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(23))
    cash: Mapped[int] = mapped_column(default=0)
    count_messages: Mapped[int] = mapped_column(default=0)
    daily: Mapped[int] = mapped_column(nullable=True)
    marry: Mapped[bool] = mapped_column(default=False)

class VoiceActivity(Base):
    __tablename__ = 'voice_activity'

    id: Mapped[int] = mapped_column(primary_key=True)
    joined_at: Mapped[int] = mapped_column(default=0)
    left_at: Mapped[int] = mapped_column(default=0)
    total_minutes: Mapped[int] = mapped_column(default=0)
    total_hours: Mapped[int] = mapped_column(default=0)

class PersonalRole(Base):
    __tablename__ = 'personal_roles'

    id: Mapped[int] = mapped_column(primary_key=True)
    owner: Mapped[int] = mapped_column()
    time: Mapped[int] = mapped_column()
    give_by_owner: Mapped[List] = mapped_column(JSON, default=[])
    shop: Mapped[bool] = mapped_column(Boolean, default=False)
    shop_cost: Mapped[int] = mapped_column(default=0)
    count_user: Mapped[int] = mapped_column(default=0)

class PersonalRoom(Base):
    __tablename__ = 'personal_rooms'

    id: Mapped[int] = mapped_column(primary_key=True)
    owner: Mapped[int] = mapped_column()
    co_owner: Mapped[int] = mapped_column(default=0)
    time: Mapped[int] = mapped_column()
    limit: Mapped[str] = mapped_column(String(2))
    personal_room: Mapped[str] = mapped_column(String(100))

class Marriage(Base):
    __tablename__ = 'marriages'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    partner_1: Mapped[int] = mapped_column()
    partner_2: Mapped[int] = mapped_column()
    time: Mapped[int] = mapped_column()
    balance: Mapped[int] = mapped_column()
    reg_marry: Mapped[str] = mapped_column(String(50))
    love_room: Mapped[str] = mapped_column(String(100))
    
class Transaction(Base):
    __tablename__ = 'transactions'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    member_id: Mapped[int] = mapped_column()
    category: Mapped[str] = mapped_column(String(50))
    value: Mapped[int] = mapped_column()
    time: Mapped[int] = mapped_column()

async def async_main():
    async with engine.begin() as conn:
        # create all classes if they don't exist
        await conn.run_sync(Base.metadata.create_all)