import datetime
from enum import Enum, auto
from typing import Any, List, Iterable

from pydantic import (
    Field,
    BaseModel,
    model_validator,
    ValidationError,
    field_validator,
    FieldValidationInfo,
    AliasPath,
    AliasChoices
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


class RadiusAttributePair(BaseModel):
    attribute: str
    value: str
    op: str = RadiusOperators[':='].value


    @field_validator("value", mode="before")
    @classmethod
    def check_value(cls, v, info: FieldValidationInfo):
        if info.data['attribute'] == RadiusAttributeType.expiration:
            if isinstance(v, datetime.datetime):
                dt = datetime.datetime.now() + datetime.timedelta(days=int(v))
                return dt.strftime(FREERADIUS_EXPIRATION_DATE_FORMAT)

        if info.data['attribute'] == RadiusAttributeType.simultaneous_use:
            return str(v)

        if info.data['attribute'] == RadiusAttributeType.password:
            return str(v)
        return v


class RadCheckModel(BaseModel):
    username: str
    attribute: str
    op: str
    value: str


class RadCheckModels(BaseModel):
    radchecks: List[RadCheckModel]

    def salam(self, objs: List):
        l = list()
        for obj in objs:
               l.append(RadCheckModel(obj.to_dict()))

    @classmethod
    def create_radchecks_model(cls, user):
        d = {
            RadiusAttributeType.password: RadiusAttributePair(attribute=RadiusAttributeType.password, value=user.password),
            RadiusAttributeType.expiration: RadiusAttributePair(attribute=RadiusAttributeType.expiration, value=user.plan_period),
        }
        if user.max_clients > 0:
            d.update({RadiusAttributeType.simultaneous_use: RadiusAttributePair(attribute=RadiusAttributeType.simultaneous_use, value=user.max_clients)})

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

