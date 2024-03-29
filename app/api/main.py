import datetime

import sqlalchemy
from typing import Union
from fastapi import BackgroundTasks, Depends, HTTPException, status, Security, BackgroundTasks
from fastapi.responses import PlainTextResponse


from app import app
from app.radius import radcheck
from app.utils.openvpn import OpenVPNConfigFile
from .schema import User, UserCreateResponse, UserGetResponse, UserUsage, UserRenew, DetailsUsage, UserRenewResponse
from app.database import get_db, AsyncSession, GetSessionDB
from .auth import get_api_key
from app.database.model import *
from app.database.query import (
    create_user_db,
    get_user_db,
    total_usage,
    query_download_upload_daily,
    renew_user_db,
    UserExists,
    UserNotFoundError,
    ServerNotFound,
    remove_accounting_data
)


@app.post("/user/create", response_model=UserCreateResponse)
async def create_user(user: User, db: AsyncSession = Depends(get_db), api_key: str = Security(get_api_key)):
    """
    Create a user
    - **username** str
    - **password** is string

    """
    try:
        await create_user_db(user, db)
    except UserExists:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User exists.")

    expire_date = radcheck.PlanPeriodToDatetime(user.plan_period).date_datetime
    return UserCreateResponse(**user.model_dump(), expire=expire_date)


@app.put("/user")
async def update_user(user: User, db: AsyncSession = Depends(get_db), api_key: str = Security(get_api_key)):
    pass


@app.post("/user/renew")
async def renew_user(
        user: UserRenew,
        db: AsyncSession = Depends(get_db),
        api_key: str = Security(get_api_key)
) -> UserRenewResponse:

    try:
        await renew_user_db(user, db)
    except UserNotFoundError:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User not found.")

    expire_date = radcheck.PlanPeriodToDatetime(user.plan_period).date_datetime
    return UserRenewResponse(**user.model_dump(), expire=expire_date)


@app.get("/user/{username}/get")
async def get_user(username: str, db: AsyncSession = Depends(get_db), api_key: str = Security(get_api_key)):
    result = await get_user_db(username, db)
    if len(result.radchecks) == 0:
        raise HTTPException(status_code=status.HTTP_410_GONE, detail="User not found in database.")
    return UserGetResponse.convert(result)


@app.get("/stats/{username}/overall", response_model=UserUsage)
async def overall_stats(username: str, db: AsyncSession = Depends(get_db), api_key: str = Security(get_api_key)):
    return await total_usage(username=username, session=db)


@app.get("/stats/{username}/details", response_model=DetailsUsage)
async def details_stats(username: str, db: AsyncSession = Depends(get_db), api_key: str = Security(get_api_key)):
    usages = await query_download_upload_daily(username=username, session=db)
    return usages


@app.post("/stats/{username}/reset")
async def reset_stats(username: str, db: AsyncSession = Depends(get_db), api_key: str = Security(get_api_key)):
    await remove_accounting_data(username, db)


@app.get("/download/openvpn/{token}")
async def download_openvpn_config(token: str, db: AsyncSession = Depends(get_db)):
    try:
        response = await OpenVPNConfigFile(token=token).stream_response(db)
        return response
    except ServerNotFound as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Server not found. Server IP: {e.server_ip}")


@app.get("/admin", response_class=PlainTextResponse)
async def download_file_with_api_key(api_key: str = Security(get_api_key)):
    await GetSessionDB.create_all()
    return OpenVPNConfigFile().text_response()


@app.get("/protected")
def proc(api_key: str = Security(get_api_key)):
    return {"message": "Access granted."}
