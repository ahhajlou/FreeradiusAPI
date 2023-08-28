import datetime
from typing import List
from pydantic import (
    Field,
    BaseModel,
    field_validator,
    model_validator
)

from config import FREERADIUS_EXPIRATION_DATE_FORMAT
from app.radius import radcheck
from app.utils.openvpn import OpenVPNConfigFile


class User(BaseModel):
    username: str
    password: str
    plan_period: int = Field(gt=0, description="Plan period should be greater than zero.")
    traffic: int = Field(gt=-1, description="Traffic can be 0 or greater. 0 means unlimited")  # 0 means unlimited
    max_clients: int = Field(gt=-1, description="max clients can be 0 or greater. 0 means unlimited")  # 0 means unlimited
    server_ip_address: str


class UserCreateResponse(BaseModel):
    username: str
    password: str
    expire: datetime.datetime
    max_clients: int
    server_ip_address: str
    config_file_url: str = ""

    @model_validator(mode='after')
    def create_link(self):
        if not self.config_file_url:
            self.config_file_url = OpenVPNConfigFile(username=self.username, server="s1").download_url()  # TODO: temporary, complete it
        return self

    @classmethod
    def load_from_database(cls):
        pass


# class UserModify(BaseModel):
#     username: str
#     password: str


class UserGetResponse(BaseModel):
    username: str
    password: str
    expire: datetime.datetime
    max_clients: int | None = None
    config_file_url: str = ""

    @model_validator(mode='after')
    def create_link(self):
        if not self.config_file_url:
            self.config_file_url = OpenVPNConfigFile(username=self.username, server="s1").download_url()  # TODO: temporary, complete it
        return self

    @classmethod
    def convert(cls, models):
        d = dict()
        d.update(username=models.radchecks[0].username)
        for model in models.radchecks:
            if model.attribute == radcheck.RadiusAttributeType.password:
                d.update(password=model.value)

            if model.attribute == radcheck.RadiusAttributeType.expiration:
                d.update(expire=datetime.datetime.strptime(model.value, FREERADIUS_EXPIRATION_DATE_FORMAT))

            if model.attribute == radcheck.RadiusAttributeType.simultaneous_use:
                d.update(max_clients=model.value)

        return cls.model_validate(d)


class UserRenew(BaseModel):
    username: str
    password: str
    plan_period: int = Field(gt=0, description="Plan period should be greater than zero.")


class DailyUsage(BaseModel):
    uploads: int
    downloads: int
    date: datetime.datetime


class DetailsUsage(BaseModel):
    usages: List[DailyUsage]


class UserUsage(BaseModel):  # store user download and upload usage
    download: int
    upload: int

    @field_validator("*", mode="before")  # the value may be 0 if the user has not connected yet  # noqa
    @classmethod
    def convert_to_zero(cls, v: int | None) -> int:
        if v is None:
            return 0
        return v
