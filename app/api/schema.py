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

from config import FREERADIUS_EXPIRATION_DATE_FORMAT
from app.radius import radcheck


class User(BaseModel):
    username: str
    password: str
    plan_period: int = Field(gt=0, description="Plan period should be greater than zero.")
    traffic: int = Field(gt=-1, description="Traffic can be 0 or greater.")
    max_clients: int


class UserCreateResponse(BaseModel):
    username: str
    password: str
    expire: datetime.datetime
    max_clients: int
    config_file_url: str | None = None

    @model_validator(mode='after')
    def create_link(self):
        self.config_file_url = "https://google.com"
        return self

    @classmethod
    def load_from_database(cls):
        pass


class UserGetResponse(BaseModel):
    username: str
    password: str
    expire: datetime.datetime
    max_clients: int

    @classmethod
    def convert(cls, models):
        d = dict()
        d.update(username=models[0].username)
        for model in models:
            if model.attribute == radcheck.RadiusAttributeType.password:
                d.update(password=model.value)

            if model.attribute == radcheck.RadiusAttributeType.expiration:
                d.update(expire=datetime.datetime.strptime(model.value, FREERADIUS_EXPIRATION_DATE_FORMAT))

            if model.attribute == radcheck.RadiusAttributeType.simultaneous_use:
                d.update(max_clients=model.value)

        return cls.model_validate(d)


class DailyUsage(BaseModel):
    uploads: int
    downloads: int
    date: datetime.datetime


class DetailsUsage(BaseModel):
    usages: List[DailyUsage]


class UserUsage(BaseModel):  # store user' download and upload usage
    download: int
    upload: int

    @field_validator("*", mode="before")  # the value may be 0 if the user has not connected yet
    @classmethod
    def convert_to_zero(cls, v: int | None) -> int:
        if v is None:
            return 0
        return v
