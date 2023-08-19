from enum import Enum
from pydantic import BaseModel, TypeAdapter
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text, func, asc, desc, select, and_, func

from . import GetSessionDB

from app.database.model import RadCheck
from app.api.model import User, UserGetResponse
from app.radius.radcheck import RadCheckModel, GenerateRadCheckModels, RasdCheckTest


async def create_user_db(user: User, session: AsyncSession):
    radchecks_list = GenerateRadCheckModels(user=user)
    radchecks_list.gen()

    async with session.begin():
        for radcheck in radchecks_list.radchecks:
            session.add(
                RadCheck(
                    **radcheck.model_dump()
                )
            )


async def get_user_db(username: str, session: AsyncSession):
    stmt = select(RadCheck).where(RadCheck.username == username)
    result = await session.execute(stmt)
    print(RasdCheckTest.model_validate(result.scalars().all()))
    pass

    models = []
    # out = TypeAdapter(List[RadCheckModel]).validate_python(result.scalars())
    for r in result.scalars().all():
        # print(r.to_dict())
        # print(RadCheckModel.model_validate(r.to_dict()))
        try:
            print(RasdCheckTest.model_validate(r))
        #     # print(TypeAdapter(RadCheckModel).validate_python(r.to_dict()))
        #     print(RasdCheckTest.model_validate(r.to_dict()))
        except:
            print("error")
        continue
        try:
            print(r.to_dict())
            models.append(
                RadCheckModel(
                    username=r.username,
                    attribute=r.attribute,
                    op=r.op,
                    value=r.value
                )
            )
        except:
            continue


#
# async def query_download_daily(user: User):
#     asyncwith GetSessionDB() as session:
#         stmt = select(
#                 RadAcct.acctstarttime,
#                 func.sum(RadAcct.acctoutputoctets).label('downloads'),
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
# async def total(user: User):
#     with GetSessionDB() as session:
#         subq = select(
#                 func.sum(RadAcct.acctoutputoctets).label('downloads'),
#                 func.sum(RadAcct.acctinputoctets).label('uploads')
#             ).where(
#                 and_(RadAcct.username==user.username, RadAcct.acctstoptime > 0)
#             ).subquery()
#
#         stmt = select(func.sum(subq.c.downloads), func.sum(subq.c.uploads))
#         result = await session.execute(stmt)
#         return result.scalar_one()
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
#
# class CalculateUsageAll:
#     def __init__(self):
#         pass
#
#     def test(self, user: User):
#         with GetSessionDB()as session:
#             subq = select(
#                     func.sum(RadAcct.acctoutputoctets).label('downloads'),
#                     func.sum(RadAcct.acctinputoctets).label('uploads')
#                 ).where(
#                     and_(RadAcct.username==user.username, RadAcct.acctstoptime > 0)
#                 ).subquery()
#
#             stmt = select(func.sum(subq.c.downloads).label('download'), func.sum(subq.c.uploads).label('upload'))
#             result = await session.scalars(stmt).first()
#
#             return UserUsage(**result._mapping)
#             #return result.scalar()
#             #return result.scalar_one()
#             #return result.scalar()
#
#     def upload(self):
#         pass
#
#     def download(self):
#         pass
#
#     def total(self):
#         pass
#
#     async def exec(self):
#         result = UserUsage()
