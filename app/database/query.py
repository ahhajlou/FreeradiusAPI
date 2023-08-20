import datetime
from typing import List
from pydantic import BaseModel, TypeAdapter
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text, func, asc, desc, select, and_, func, bindparam, update


from app.database.model import RadCheck, RadAcct
from app.api.schema import User, UserGetResponse, UserUsage, DailyUsage, DetailsUsage
from app.radius.radcheck import RadCheckModel, RadCheckModels, get_value_by_attr_type, RadiusAttributeType, PlanPeriodToDatetime, FreeradiusStrDatetimeHelper


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
    return RadCheckModels.load_from_db(result.scalars().all())


async def renew_user_db(user: User, session: AsyncSession):
    stmt = select(RadCheck).where(RadCheck.username == user.username)
    result = await session.execute(stmt)
    radchecks = result.scalars().all()
    if len(radchecks) == 0:
        raise Exception

    for radcheck in radchecks:
        if radcheck.attribute == RadiusAttributeType.expiration.value:
            _expire_date = FreeradiusStrDatetimeHelper.from_str_to_datetime(radcheck.value)
            if _expire_date > datetime.datetime.now():
                _expire_date += PlanPeriodToDatetime(period=user.plan_period).get_timedelta()
            else:
                _expire_date = PlanPeriodToDatetime(period=user.plan_period).date_datetime

            radcheck.value = FreeradiusStrDatetimeHelper.from_datetime_to_str(_expire_date)

        if radcheck.attribute == RadiusAttributeType.password:
            if radcheck.value != user.password:
                radcheck.value = user.password

        if radcheck.attribute == RadiusAttributeType.simultaneous_use:
            if radcheck.value != user.max_clients and user.max_clients > 0:
                radcheck.value = user.max_clients

    await session.commit()





# async def renew_user_db(user: User, session: AsyncSession):
#     stmt = update(RadCheck)\
#         .where( and_(RadCheck.username == user.username, RadCheck.attribute == RadiusAttributeType.password.value, RadCheck.value == bindparam("oldpass")))\
#                .values(value=bindparam("newpass"))#.execution_options(synchronize_session="fetch")
#     print(stmt)
#     await session.execute(
#         stmt,
#         [
#             {"oldpass": "newpassword", "newpass": "salam"}
#         ],
#         execution_options={"synchronize_session": False}
#     )
#     return
    # stmt = select(RadCheck).where(RadCheck.username == user.username)
    # result = await session.execute(stmt)
    # radchecks = result.scalars().all()
    # if len(radchecks) == 0:
    #     raise Exception
    #
    # models = RadCheckModels.load_from_db(radchecks)
    #
    # if user.max_clients > 0:
    #     v = get_value_by_attr_type(RadiusAttributeType.simultaneous_use, models)
    #     print(v)
    # expire_date = get_value_by_attr_type(RadiusAttributeType.expiration, models)

    # if expire_date > datetime.datetime.now():
    #     expire_date += (RadCheckModel.expitration)
    # else:
    #     expire_date = RadCheckModel.expiration
    #
    # await session.commit()


async def query_download_upload_daily(username: str, session: AsyncSession) -> DetailsUsage:
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

    daily_usages = TypeAdapter(List[DailyUsage]).validate_python(list(map(lambda v: v._mapping, result)))
    return DetailsUsage(usages=daily_usages)


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
