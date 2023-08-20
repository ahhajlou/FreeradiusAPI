from sqlalchemy.ext.asyncio import AsyncSession
from .base import async_session, engine, Base

# from .model import User  # fix alembic autogenerate revision issue


class GetSessionDB:  # Async context manager
    def __init__(self):
        self.session = async_session()

    async def __aenter__(self) -> AsyncSession:
        return self.session

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        # for AsyncEngine created in function scope, close and
        # clean-up pooled connections
        await engine.dispose()
    @staticmethod
    async def create_all():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)


async def get_db():  # for fastapi "Depends"
    # db = async_session()
    # try:
    #     yield db
    # finally:
    #     await db.close()
    async with GetSessionDB() as db:
        yield db
