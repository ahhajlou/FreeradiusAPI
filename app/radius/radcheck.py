import datetime
from enum import Enum, auto
from typing import Any

from pydantic import BaseModel, model_validator, ValidationError, field_validator, FieldValidationInfo

from app.api.model import User

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


class RadiusAttribute(str, Enum):
    password: str = PasswordType.clear_text.value
    expiration: str = "Expiration"
    simultaneous_use: str = "Simultaneous-Use"


class RadiusAttributePair(BaseModel):
    attribute: RadiusAttribute
    value: str


class RadCheckModel(BaseModel):
    user: User | str
    attribute: RadiusAttribute | str
    op: RadiusOperators | str = RadiusOperators[':=']
    value: str | None = None


    @field_validator("attribute", mode="after")
    @classmethod
    def attribute_convertor(cls, v: RadiusAttribute | str, info: FieldValidationInfo):
        if isinstance(v, str):  # from db
            return RadiusAttribute(v)
        return v.value

    @field_validator("op", mode="after")
    @classmethod
    def attribute_convertor(cls, v: RadiusOperators | str, info: FieldValidationInfo):
        if isinstance(v, str):
            return RadiusOperators(v)
        elif isinstance(v, RadiusOperators):
            return v.value




    @model_validator(mode='after')
    def radius_validator(self):
        if self.attribute == RadiusAttribute.password:
            self.value = self.user.password

        if self.attribute == RadiusAttribute.expiration:
            if not isinstance(self.user.expire, datetime.datetime):
                raise ValueError("The value is not datetime.")
            self.value = self.user.expire.strftime('%Y-%m-%d')

        return self

    def model_dump(self, *args, **kwargs) -> dict[str, Any]:
        result = dict()
        result.update(
            username=self.user.username,
            attribute=self.attribute.value,
            op=self.op.value,
            value=self.value
        )
        return result
