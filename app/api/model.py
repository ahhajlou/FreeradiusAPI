import datetime
from typing import List
from pydantic import (
    Field,
    BaseModel,
    FieldValidationInfo,
    ValidationError,
    field_validator
)


class User(BaseModel):
    username: str
    password: str
    expire: int | datetime.datetime
    limit: int = Field(gt=-1, description="data_limit can be 0 or greater")
    max_clients: int | None = None

    @field_validator("expire", mode="before")
    @classmethod
    def username_valid(cls, v: int, info: FieldValidationInfo) -> datetime.datetime:
        print(type(v))
        if not isinstance(v, int):
            raise ValueError("Int")
        print("->", info.field_name)
        print(datetime.datetime.now() + datetime.timedelta(days=v))
        return datetime.datetime.now() + datetime.timedelta(days=v)


class Download(BaseModel):
    download: int


class Upload(BaseModel):
    upload: int


class DailyUsage(BaseModel):
    upload: Download
    download: Download
    date: datetime


class DetailsUsage(BaseModel):
    usage: List[DailyUsage]


class UserUsage(BaseModel):  # store user' download and upload usage
    download: int
    upload: int

    @field_validator("*", mode="before")  # the value may be 0 if the user has not connected yet
    @classmethod
    def convert_to_zero(cls, v: int | None) -> int:
        if v is None:
            return 0
        return v