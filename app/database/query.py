import datetime
from typing import List
from pydantic import BaseModel, TypeAdapter
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text, func, asc, desc, select, and_, func, bindparam, update


from app.database.model import RadCheck, RadAcct
from app.api.schema import User, UserUsage, DailyUsage, DetailsUsage, UserRenew
from app.radius.radcheck import RadCheckModels, RadiusAttributeType, PlanPeriodToDatetime, FreeradiusStrDatetimeHelper


class UserExists(Exception):
    pass


class UserNotFoundError(Exception):
    pass


async def create_user_db(user: User, session: AsyncSession):
    radchecks_list = RadCheckModels.create_radchecks_model(user=user)  # noqa
    stmt = select(func.count()).where(RadCheck.username == user.username)

    async with session.begin():
        result = await session.execute(stmt)
        if result.scalar() > 0:
            raise UserExists
        for radcheck in radchecks_list.radchecks:  # noqa
            session.add(
                RadCheck(
                    **radcheck.model_dump()
                )
            )


async def get_user_db(username: str, session: AsyncSession) -> RadCheckModels:
    stmt = select(RadCheck).where(RadCheck.username == username)
    result = await session.execute(stmt)
    return RadCheckModels.load_from_db(result.scalars().all())


async def renew_user_db(user: UserRenew, session: AsyncSession):
    stmt = select(RadCheck).where(RadCheck.username == user.username)
    result = await session.execute(stmt)
    radchecks = result.scalars().all()  # noqa
    if len(radchecks) == 0:
        raise UserNotFoundError

    for radcheck in radchecks:  # noqa
        print(radcheck.to_dict())
        if radcheck.attribute == RadiusAttributeType.expiration.value:  # noqa
            _expire_date = FreeradiusStrDatetimeHelper.from_str_to_datetime(radcheck.value)
            if _expire_date > datetime.datetime.now():
                _expire_date += PlanPeriodToDatetime(period=user.plan_period).get_timedelta()
            else:
                _expire_date = PlanPeriodToDatetime(period=user.plan_period).date_datetime

            radcheck.value = FreeradiusStrDatetimeHelper.from_datetime_to_str(_expire_date)

        if radcheck.attribute == RadiusAttributeType.password:
            if radcheck.value != user.password:
                radcheck.value = user.password

        # if radcheck.attribute == RadiusAttributeType.simultaneous_use:
        #     if radcheck.value != user.max_clients and user.max_clients > 0:
        #         radcheck.value = user.max_clients

    await session.commit()


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

    daily_usages = TypeAdapter(List[DailyUsage]).validate_python(list(map(lambda v: v._mapping, result))) # noqa
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
    return UserUsage(**result.one()._mapping)  # noqa
