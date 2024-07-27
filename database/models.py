from sqlalchemy import String, Boolean, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine

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

async def async_main():
    async with engine.begin() as conn:
        # create all classes if they don't exist
        await conn.run_sync(Base.metadata.create_all)