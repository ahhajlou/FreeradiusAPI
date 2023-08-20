from enum import Enum
from pydantic import BaseModel, TypeAdapter
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text, func, asc, desc, select, and_, func

from . import GetSessionDB

from app.database.model import RadCheck, RadAcct
from app.api.model import User, UserGetResponse, UserUsage, DailyUsage, DetailsUsage
from app.radius.radcheck import RadCheckModel, RadCheckModels


async def create_user_db(user: User, session: AsyncSession):
    radchecks_list = RadCheckModels.create_radchecks_model(user=user)

    async with session.begin():
        print(radchecks_list)
        for radcheck in radchecks_list.radchecks:
            print(radcheck)
            session.add(
                RadCheck(
                    **radcheck.model_dump()
                )
            )


async def get_user_db(username: str, session: AsyncSession) -> RadCheckModels:
    stmt = select(RadCheck).where(RadCheck.username == username)
    result = await session.execute(stmt)
    models = RadCheckModels.load_from_db(result.scalars().all())
    return models


#
async def query_download_upload_daily(username: str, session: AsyncSession):
    stmt = select(
            RadAcct.acctstarttime.label('date'),
            func.sum(RadAcct.acctinputoctets).label('uploads'),
            func.sum(RadAcct.acctoutputoctets).label('downloads'),
        ).where(
            and_(RadAcct.username == username, RadAcct.acctstoptime > 0)
        ).group_by(
            func.day(RadAcct.acctstarttime)
        ).order_by(
            desc(RadAcct.acctstarttime)
        )

    result = await session.execute(stmt)

    # FIRST METHOD
    daily_usages = TypeAdapter(List[DailyUsage]).validate_python(list(map(lambda v: v._mapping, result)))
    detail_usages = DetailsUsage(usages=daily_usages)

    # SECOND METHOD
    DetailsUsage(usages=list(map(lambda v: DailyUsage.model_validate(v._mapping), result)))

    return TypeAdapter(List[DailyUsage]).validate_python(list(map(lambda v: v._mapping, result)))
    # TypeAdapter(List[DailyUsage]).dump_python()


# async def query_upload_daily(user: User):
#     with GetSessionDB() as session:
#         stmt = select(
#                 RadAcct.acctstarttime,
#                 func.sum(RadAcct.acctinputoctets).label('upload')
#             ).where(
#                 and_(RadAcct.username==user.username, RadAcct.acctstoptime > 0)
#             ).group_by(
#                 func.day(RadAcct.acctstarttime)
#             ).order_by(
#                 desc(RadAcct.acctstarttime)
#             )
#
#         result = await session.execute(stmt)
#
#
async def total_usage(username: str, session: AsyncSession) -> UserUsage:
    subq = select(
            func.sum(RadAcct.acctoutputoctets).label('downloads'),
            func.sum(RadAcct.acctinputoctets).label('uploads')
        ).where(
            and_(RadAcct.username == username, RadAcct.acctstoptime > 0)
        ).subquery()

    stmt = select(func.sum(subq.c.downloads).label('download'), func.sum(subq.c.uploads).label('upload'))
    result = await session.execute(stmt)
    return UserUsage(**result.one()._mapping)
#
#
# class UsageType(str, Enum):
#     download: str = "download"
#     upload: str = "upload"
#     total: str = "total"
#
#
# class ColumnSelect(Enum):
#     downloads = RadAcct.acctoutputoctets
#     uploads = RadAcct.acctinputoctets
#

