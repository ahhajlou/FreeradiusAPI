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

# from app.api import model
import typing


Date = typing.TypeVar("Date")
Limit = typing.TypeVar("Limit")
# GEN = typing.TypeVar("GEN", Date, Limit)

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
    def check_values(cls, v: Any, info: FieldValidationInfo):
        if info.data['attribute'] == RadiusAttributeType.expiration.value:
            dt = datetime.datetime.now() + datetime.timedelta(days=int(v))
            return dt.strftime('%Y-%m-%d')
        return v

    # @field_validator("attribute", mode="before")
    # @classmethod
    # def atrribute_from_db(cls, v: str):
    #     if not isinstance(v, (str, RadiusAttributeType)):
    #         raise ValueError("attribute should be either RadiusAttributeType or str.")
    #     if isinstance(v, str):
    #         return RadiusAttributeType(v)
    #     return v

    @model_validator(mode="after")
    def check_all(self):
        if self.attribute == RadiusAttributeType.password:
            self.value = RadiusAttributeType.password.value

        # if self.attribute == RadiusAttributeType.expiration:
        #     self.value = (datetime.datetime.now() + datetime.timedelta(days=int(self.value))).strftime('%Y-%m-%d')
            # if isinstance(self.value, datetime.datetime):
            #     self.value = self.value.strftime('%Y-%m-%d')
            # else:
            #     self.value = datetime.datetime.strptime(self.value, '%Y-%m-%d')


    # @field_validator("op", mode="after")
    # @classmethod
    # def attribute_convertor(cls, v: RadiusOperators | str, info: FieldValidationInfo):
    #     return ":="
    #     if isinstance(v, str):
    #         return RadiusOperators(v)
    #     else:
    #         return v.value


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
    def dmp(cls, user):
        l = list()
        for attr in RadiusAttributeType:
            print(attr)
            if value := user.get_field_by_annotated_type(attr):
                print(True)
                l.append(
                    RadCheckModel(
                        username=user.username,
                        **RadiusAttributePair(
                            attribute=attr.value,
                            value=value,
                        ).model_dump()
                    )
                )
        print(l)
        return cls(radchecks=l)

