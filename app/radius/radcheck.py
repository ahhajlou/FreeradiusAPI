import datetime
from enum import Enum
from typing import List

from pydantic import (
    BaseModel,
    field_validator,
    FieldValidationInfo,
)

from config import FREERADIUS_EXPIRATION_DATE_FORMAT

RadiusOperators = Enum(
    "RadiusOperators", {
        "==": "==",
        ":=": ":=",
        "=": "="
    }
)


class PasswordType(str, Enum):
    clear_text = "Cleartext-Password"
    nt = "NT-Password"
    md5 = "MD5-Password"
    sha1 = "SHA1-Password"
    crypt = "Crypt-Password"


class RadiusAttributeType(str, Enum):
    # TODO: in future make password field options better
    # password: PasswordType | str = PasswordType.clear_text
    password: str = "Cleartext-Password"
    expiration: str = "Expiration"
    simultaneous_use: str = "Simultaneous-Use"
    monthly_bandwidth = "Monthly-Bandwidth"


class PlanPeriodToDatetime:
    def __init__(self, period: int):
        if not isinstance(period, int):
            raise ValueError("Input parameter is not int.")
        self._period = period
        self._date = datetime.datetime.now() + datetime.timedelta(days=period)

    @property
    def date_str(self) -> str:
        return self._date.strftime(FREERADIUS_EXPIRATION_DATE_FORMAT)

    @property
    def date_datetime(self) -> datetime.datetime:
        return self._date

    def get_timedelta(self) -> datetime.timedelta:
        return datetime.timedelta(days=self._period)


class FreeradiusStrDatetimeHelper:
    @staticmethod
    def from_str_to_datetime(date_str: str) -> datetime.datetime:
        if not isinstance(date_str, str):
            raise ValueError("The date is not str.")
        return datetime.datetime.strptime(date_str, FREERADIUS_EXPIRATION_DATE_FORMAT)

    @staticmethod
    def from_datetime_to_str(date_datetime: datetime.datetime) -> str:
        if not isinstance(date_datetime, datetime.datetime):
            raise ValueError("The date is not datetime.")
        return date_datetime.strftime(FREERADIUS_EXPIRATION_DATE_FORMAT)


class RadiusAttributePair(BaseModel):
    attribute: str
    value: str
    op: str = RadiusOperators[':='].value

    @field_validator("value", mode="before")
    @classmethod
    def check_value(cls, v, info: FieldValidationInfo):
        if info.data['attribute'] == RadiusAttributeType.expiration:
            if isinstance(v, int):
                return PlanPeriodToDatetime(v).date_str

        if info.data['attribute'] == RadiusAttributeType.simultaneous_use:
            return str(v)

        if info.data['attribute'] == RadiusAttributeType.password:
            return str(v)

        if info.data['attribute'] == RadiusAttributeType.monthly_bandwidth:
            return str(v)

        return v


class RadCheckModel(BaseModel):
    username: str
    attribute: str
    op: str
    value: str


class RadCheckModels(BaseModel):
    radchecks: List[RadCheckModel]

    @classmethod
    def create_radchecks_model(cls, user):
        d = {
            RadiusAttributeType.password: RadiusAttributePair(attribute=RadiusAttributeType.password, value=user.password),
            RadiusAttributeType.expiration: RadiusAttributePair(attribute=RadiusAttributeType.expiration, value=user.plan_period),
        }
        if user.max_clients > 0:
            d.update({RadiusAttributeType.simultaneous_use: RadiusAttributePair(attribute=RadiusAttributeType.simultaneous_use, value=user.max_clients)})

        if user.traffic > 0:
            d.update({RadiusAttributeType.monthly_bandwidth: RadiusAttributePair(attribute=RadiusAttributeType.monthly_bandwidth, value=user.traffic)})

        l = list()
        for v in d.values():
                l.append(
                    RadCheckModel(
                        username=user.username,
                        **v.model_dump()
                    )
                )
        return cls(radchecks=l)

    @classmethod
    def load_from_db(cls, objs):
        l = list()
        for obj in objs:
            l.append(
                RadCheckModel(
                    **obj.to_dict()
                )
            )
        return cls(radchecks=l)

