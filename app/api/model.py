import datetime
from typing import List
from pydantic import (
    Field,
    BaseModel,
    FieldValidationInfo,
    ValidationError,
    field_validator,
    model_validator
)


class User(BaseModel):
    username: str
    password: str
    expire: int | datetime.datetime
    limit: int = Field(gt=-1, description="data_limit can be 0 or greater")
    max_clients: int | None = None

    @field_validator("expire", mode="after")
    @classmethod
    def username_valid(cls, v: int, info: FieldValidationInfo) -> datetime.datetime:
        if isinstance(v, datetime.datetime):
            return v
        return datetime.datetime.now() + datetime.timedelta(days=v)


class UserCreateResponse(BaseModel):
    username: str
    password: str
    expire: datetime.datetime
    limit: int
    config_file_url: str | None = None

    @model_validator(mode='after')
    def create_link(self):
        self.config_file_url = "https://google.com"
        return self


class UserGetResponse(BaseModel):
    username: str
    password: str
    expire: datetime.datetime
    limit: int


# class Download(BaseModel):
#     download: int
#
#
# class Upload(BaseModel):
#     upload: int
#
#
# class DailyUsage(BaseModel):
#     upload: Download
#     download: Download
#     date: datetime
#
#
# class DetailsUsage(BaseModel):
#     usage: List[DailyUsage]
#
#
# class UserUsage(BaseModel):  # store user' download and upload usage
#     download: int
#     upload: int
#
#     @field_validator("*", mode="before")  # the value may be 0 if the user has not connected yet
#     @classmethod
#     def convert_to_zero(cls, v: int | None) -> int:
#         if v is None:
#             return 0
#         return v