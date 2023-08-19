import datetime
import typing
from typing import List
from pydantic import (
    Field,
    BaseModel,
    FieldValidationInfo,
    ValidationError,
    field_validator,
    model_validator
)

from app.radius import radcheck


class User(BaseModel):
    username: str
    password: typing.Annotated[str, radcheck.RadiusAttributeType.password]
    plan_period: typing.Annotated[int, radcheck.RadiusAttributeType.expiration]
    traffic: int = Field(gt=-1, description="traffic can be 0 or greater")
    max_clients: typing.Annotated[int, radcheck.RadiusAttributeType.simultaneous_use]

    def get_field_by_annotated_type(self, tp):
        print(self.__annotations__.items())
        for k, v in self.__annotations__.items():
            print(f"{k} --- {v}")
            try:
                if tp == typing.get_args(v)[1]:
                    print("Dumped model::::::", self.model_dump(), '-f-f-f', typing.get_args(v), " - ", k)
                    return self.model_dump()[k]
            except IndexError:
                continue
        print("%%%%_______%%%%%")

    # @field_validator("expire", mode="after")
    # @classmethod
    # def username_valid(cls, v: int, info: FieldValidationInfo) -> datetime.datetime:
    #     if isinstance(v, datetime.datetime):
    #         return v
    #     return datetime.datetime.now() + datetime.timedelta(days=v)


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